from rest_framework import serializers
from academics.models import StudentProfile
from sessions.models import ClassSession
from .models import AttendanceRecord, AttendanceVerificationEvent, StudentDeviceRegistration

class GatewayAttendanceEventSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    student_id = serializers.UUIDField(required=False)
    device_token_hash = serializers.CharField(required=False)
    session_id = serializers.UUIDField()
    event_type = serializers.ChoiceField(choices=AttendanceVerificationEvent.EventType.choices)

    def validate(self, data):
        if data.get('event_type') == AttendanceVerificationEvent.EventType.RFID and not data.get('student_id'):
            raise serializers.ValidationError("RFID events must include student_id")
        if data.get('event_type') == AttendanceVerificationEvent.EventType.PROXIMITY and not data.get('device_token_hash'):
            raise serializers.ValidationError("Proximity events must include device_token_hash")
        return data
