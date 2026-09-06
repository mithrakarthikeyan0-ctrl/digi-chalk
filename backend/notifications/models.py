from django.db import models
from django.conf import settings
from common.models import UUIDTimeStampedModel
from academics.models import StudentProfile, ParentProfile
from ews.models import InterventionCase

class CommunicationPreference(UUIDTimeStampedModel):
    """
    Stores communication preferences for a parent.
    """
    class Language(models.TextChoices):
        EN = 'en', 'English'
        TA = 'ta', 'Tamil'
        HI = 'hi', 'Hindi'
        GU = 'gu', 'Gujarati'
        
    parent = models.OneToOneField(ParentProfile, on_delete=models.CASCADE, related_name='communication_preference')
    preferred_language = models.CharField(max_length=10, choices=Language.choices, default=Language.EN)
    allowed_channels = models.CharField(max_length=255, default='in_app', help_text="Comma-separated list of allowed channels (e.g., sms,whatsapp,email,in_app)")
    consent_status = models.BooleanField(default=False)
    consent_captured_at = models.DateTimeField(null=True, blank=True)
    do_not_contact = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Communication Preference'
        verbose_name_plural = 'Communication Preferences'

    def __str__(self):
        return f"Prefs for {self.parent.user.full_name}"

class NotificationTemplate(UUIDTimeStampedModel):
    """
    Stores multilingual templates for parent communications.
    """
    template_key = models.CharField(max_length=100, db_index=True)
    channel = models.CharField(max_length=50) # e.g. 'sms', 'whatsapp', 'email', 'in_app'
    language = models.CharField(max_length=10, default='en')
    title_template = models.CharField(max_length=255, blank=True)
    body_template = models.TextField()
    active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ('template_key', 'channel', 'language')

    def __str__(self):
        return f"{self.template_key} ({self.language} - {self.channel})"

class Notification(UUIDTimeStampedModel):
    """
    Represents a single outbound message.
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        QUEUED = 'queued', 'Queued'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)
    intervention_case = models.ForeignKey(InterventionCase, on_delete=models.CASCADE, null=True, blank=True)
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=50, default='in_app')
    language = models.CharField(max_length=10, default='en')
    
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_notifications')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_notifications')
    approved_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.email} - {self.get_status_display()}"

class NotificationDeliveryAttempt(UUIDTimeStampedModel):
    """
    Audit log of provider sending attempts.
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_attempts')
    provider_name = models.CharField(max_length=100)
    provider_message_id = models.CharField(max_length=255, blank=True)
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=50)
    response_metadata = models.JSONField(default=dict, blank=True) # Sanitized response
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Attempt'
        verbose_name_plural = 'Delivery Attempts'
        ordering = ['-attempted_at']

    def __str__(self):
        return f"Attempt {self.attempt_number} for Notification {self.notification.id}"
