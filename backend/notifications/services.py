import importlib
import logging
import re
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .models import Notification, NotificationDeliveryAttempt, NotificationTemplate, CommunicationPreference

logger = logging.getLogger(__name__)


def get_provider_class(provider_path: str):
    """Dynamically load the provider class from settings string."""
    module_path, class_name = provider_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_provider_for_channel(channel: str):
    provider_path = settings.NOTIFICATION_PROVIDERS.get(channel, settings.NOTIFICATION_PROVIDERS['default'])
    provider_class = get_provider_class(provider_path)
    return provider_class()


def safe_format(template_str: str, context: dict) -> str:
    """
    Safely formats a string by replacing {{ variable }} with context values.
    Does not allow execution of code.
    """
    if not template_str:
        return ""
        
    def replace_func(match):
        key = match.group(1).strip()
        return str(context.get(key, f"{{{{{key}}}}}"))
        
    return re.sub(r'\{\{(.*?)\}\}', replace_func, template_str)


def can_send_notification(notification: Notification) -> bool:
    """
    Checks consent, opt-out, and rate limits.
    """
    if notification.status in [Notification.Status.SENT, Notification.Status.DELIVERED, Notification.Status.CANCELLED]:
        return False
        
    try:
        pref = notification.recipient.parent_profile.communication_preference
    except (AttributeError, CommunicationPreference.DoesNotExist):
        # Default to false if we don't have explicit preferences set yet
        notification.failure_reason = "No communication preferences found."
        return False

    if pref.do_not_contact:
        notification.failure_reason = "Parent opted out of all communications (do_not_contact is True)."
        return False
        
    if not pref.consent_status:
        notification.failure_reason = "Missing explicit consent."
        return False
        
    allowed_channels = [c.strip() for c in pref.allowed_channels.split(',') if c.strip()]
    if notification.channel not in allowed_channels:
        notification.failure_reason = f"Channel '{notification.channel}' not in allowed list."
        return False

    # Cooldown check: No more than 1 notification per hour to the same parent on the same channel
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent = Notification.objects.filter(
        recipient=notification.recipient,
        channel=notification.channel,
        status__in=[Notification.Status.SENT, Notification.Status.DELIVERED],
        sent_at__gte=one_hour_ago
    ).exists()
    
    if recent:
        notification.failure_reason = "Rate limit exceeded (1 per hour)."
        return False

    return True


def dispatch_notification(notification: Notification) -> bool:
    """
    Attempts to send the notification via the configured provider.
    """
    if not can_send_notification(notification):
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=['status', 'failure_reason'])
        return False

    provider = get_provider_for_channel(notification.channel)
    
    attempt = NotificationDeliveryAttempt(
        notification=notification,
        provider_name=provider.__class__.__name__,
        attempt_number=notification.delivery_attempts.count() + 1
    )
    
    try:
        success, message_id, metadata = provider.send(notification)
        attempt.status = 'success' if success else 'failed'
        attempt.provider_message_id = message_id
        attempt.response_metadata = metadata
        attempt.save()
        
        if success:
            notification.status = Notification.Status.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            return True
        else:
            notification.status = Notification.Status.FAILED
            notification.failure_reason = "Provider rejected the message."
            notification.save(update_fields=['status', 'failure_reason'])
            return False
            
    except Exception as e:
        logger.exception("Failed to dispatch notification")
        attempt.status = 'error'
        attempt.response_metadata = {"error": str(e)}
        attempt.save()
        
        notification.status = Notification.Status.FAILED
        notification.failure_reason = f"Internal error during dispatch: {str(e)}"
        notification.save(update_fields=['status', 'failure_reason'])
        return False


def create_notification_from_draft(draft, template_key: str, context: dict) -> Notification:
    """
    Creates a notification from a draft or event context.
    """
    # Assuming recipient is determined from intervention case or passed context
    intervention = draft.intervention_case
    student = intervention.risk_assessment.student
    
    # Try to get parent link
    parent_link = student.parent_links.first()
    if not parent_link:
        raise ValueError("Student has no linked parent.")
        
    parent = parent_link.parent
    
    try:
        pref = parent.communication_preference
        language = pref.preferred_language
        channel = [c.strip() for c in pref.allowed_channels.split(',') if c.strip()][0] # Pick first allowed channel
    except (AttributeError, CommunicationPreference.DoesNotExist):
        language = 'en'
        channel = 'in_app'
        
    # Find template
    template = NotificationTemplate.objects.filter(
        template_key=template_key, 
        language=language, 
        channel=channel,
        active=True
    ).first()
    
    if not template:
        # Fallback to English
        template = NotificationTemplate.objects.filter(
            template_key=template_key, 
            language='en', 
            channel=channel,
            active=True
        ).first()
        
    if not template:
        raise ValueError(f"No active template found for {template_key} on {channel}")

    # Build context
    full_context = {
        'parent_name': parent.user.full_name,
        'child_name': student.user.full_name,
        'action_required': 'Please review the portal.',
        'support_contact': 'support@school.edu',
    }
    full_context.update(context)

    title = safe_format(template.title_template, full_context)
    body = safe_format(template.body_template, full_context)

    notification = Notification.objects.create(
        recipient=parent.user,
        student=student,
        intervention_case=intervention,
        template=template,
        channel=channel,
        language=language,
        title=title,
        body=body,
        status=Notification.Status.PENDING_APPROVAL if template.requires_approval else Notification.Status.QUEUED,
        created_by=draft.approved_by # The person who approved the draft
    )
    
    return notification
