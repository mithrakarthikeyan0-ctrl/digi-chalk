import logging
import uuid
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class BaseNotificationProvider:
    """
    Interface for external notification providers.
    """
    def send(self, notification) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Sends the notification.
        Returns:
            success (bool): Whether it was successfully accepted by provider.
            message_id (str): Provider's internal ID for the message.
            metadata (dict): Sanitized response metadata.
        """
        raise NotImplementedError()


class ConsoleNotificationProvider(BaseNotificationProvider):
    """
    Local development provider that just logs to the console safely.
    """
    def send(self, notification) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"--- MOCK NOTIFICATION SENT via {notification.channel} ---")
        logger.info(f"Recipient: {notification.recipient.email}")
        logger.info(f"Language: {notification.language}")
        logger.info(f"Title: {notification.title}")
        logger.info(f"Body:\n{notification.body}")
        logger.info("---------------------------------------")
        
        return True, f"console-{uuid.uuid4()}", {"provider": "console", "status": "success"}


class SmsProviderPlaceholder(BaseNotificationProvider):
    """
    Placeholder for a real SMS provider (e.g. Twilio, AWS SNS).
    """
    def send(self, notification) -> Tuple[bool, str, Dict[str, Any]]:
        # In a real implementation, you would use os.environ to get API keys,
        # formulate the payload, and send to the provider's REST API.
        logger.info("SMS Provider Placeholder invoked. Real sending is disabled.")
        return True, f"sms-stub-{uuid.uuid4()}", {"provider": "sms_placeholder"}


class WhatsAppProviderPlaceholder(BaseNotificationProvider):
    """
    Placeholder for a WhatsApp Business API provider.
    """
    def send(self, notification) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info("WhatsApp Provider Placeholder invoked. Real sending is disabled.")
        return True, f"wa-stub-{uuid.uuid4()}", {"provider": "whatsapp_placeholder"}


class EmailProviderPlaceholder(BaseNotificationProvider):
    """
    Placeholder for an Email provider (e.g. SendGrid, Mailgun).
    """
    def send(self, notification) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info("Email Provider Placeholder invoked. Real sending is disabled.")
        return True, f"email-stub-{uuid.uuid4()}", {"provider": "email_placeholder"}
