from rest_framework import serializers
from .models import CommunicationPreference, Notification, NotificationDeliveryAttempt
from accounts.models import User

class CommunicationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationPreference
        fields = ['preferred_language', 'allowed_channels', 'consent_status', 'do_not_contact', 'consent_captured_at']
        read_only_fields = ['consent_captured_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'channel', 'language', 'status', 'created_at', 'sent_at']
        read_only_fields = fields

class NotificationDeliveryAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDeliveryAttempt
        fields = ['attempt_number', 'provider_name', 'status', 'attempted_at']
        read_only_fields = fields

class TeacherNotificationDraftSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    template_key = serializers.CharField(max_length=100)
    context = serializers.DictField()

    def validate(self, attrs):
        # Additional validation can be placed here
        return attrs
