import pytest
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from attendance.models import AttendanceRecord, AttendanceVerificationEvent, StudentDeviceRegistration

@pytest.mark.django_db
class TestAttendanceDualLayer:
    def test_dual_layer_matching(self, api_client, student_user, student_profile, classroom, teacher_user):
        from sessions.models import ClassSession
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="recording")
        
        # Setup student device
        StudentDeviceRegistration.objects.create(
            student=student_profile,
            device_token_hash="hash123"
        )
        
        url = reverse('gateway-attendance-events')
        
        # 1. Post RFID event
        api_client.credentials(HTTP_X_GATEWAY_AUTH='local-dev-gateway-key-secret')
        events = [
            {
                'event_id': 'evt_rfid_1',
                'session_id': str(session.id),
                'student_id': str(student_profile.id),
                'event_type': 'rfid'
            }
        ]
        response = api_client.post(url, {'events': events}, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Check record is pending
        record = AttendanceRecord.objects.get(student=student_profile, class_session=session)
        assert record.status == 'pending'
        
        # 2. Post Proximity event within 5 minutes
        events = [
            {
                'event_id': 'evt_prox_1',
                'session_id': str(session.id),
                'device_token_hash': 'hash123',
                'event_type': 'proximity'
            }
        ]
        response = api_client.post(url, {'events': events}, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Check record is now present
        record.refresh_from_db()
        assert record.status == 'present'
        assert record.verification_method == 'dual_factor'

    def test_idempotency_duplicate_events(self, api_client, student_user, student_profile, classroom, teacher_user):
        from sessions.models import ClassSession
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="recording")
        url = reverse('gateway-attendance-events')
        api_client.credentials(HTTP_X_GATEWAY_AUTH='local-dev-gateway-key-secret')
        
        events = [
            {
                'event_id': 'evt_dup',
                'session_id': str(session.id),
                'student_id': str(student_profile.id),
                'event_type': 'rfid'
            }
        ]
        
        # First push
        res1 = api_client.post(url, {'events': events}, format='json')
        assert res1.status_code == status.HTTP_200_OK
        assert res1.data['processed'] == 1
        
        # Second push
        res2 = api_client.post(url, {'events': events}, format='json')
        assert res2.status_code == status.HTTP_200_OK
        assert res2.data['processed'] == 0 # Event ignored
