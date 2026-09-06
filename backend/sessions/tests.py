import pytest
from rest_framework import status
from django.urls import reverse
from sessions.models import ClassSession, Bookmark

@pytest.mark.django_db
class TestSessionPermissions:
    def test_teacher_can_create_session(self, api_client, teacher_user, classroom):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": teacher_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_sessions = reverse('session-list')
        data = {
            "classroom": classroom.id,
            "status": "recording"
        }
        response = api_client.post(url_sessions, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert ClassSession.objects.filter(classroom=classroom, teacher=teacher_user).exists()

    def test_student_cannot_create_session(self, api_client, student_user, classroom):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_sessions = reverse('session-list')
        data = {
            "classroom": classroom.id,
            "status": "recording"
        }
        response = api_client.post(url_sessions, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_can_view_enrolled_session(self, api_client, student_user, enrollment, teacher_user, classroom):
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="idle")

        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_sessions = reverse('session-list')
        response = api_client.get(url_sessions)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(session.id)

    def test_teacher_can_add_bookmark(self, api_client, teacher_user, classroom):
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="recording")

        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": teacher_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_bookmark = reverse('session-add-bookmark', kwargs={'pk': session.id})
        data = {
            "timestamp_seconds": 12.5,
            "label": "Important concept"
        }
        response = api_client.post(url_bookmark, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Bookmark.objects.filter(session=session, label="Important concept").exists()

    def test_student_cannot_add_bookmark(self, api_client, student_user, enrollment, teacher_user, classroom):
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="recording")

        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_bookmark = reverse('session-add-bookmark', kwargs={'pk': session.id})
        data = {
            "timestamp_seconds": 12.5,
            "label": "Important concept"
        }
        response = api_client.post(url_bookmark, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_sync_events_gateway_auth(self, api_client, teacher_user, classroom):
        session = ClassSession.objects.create(classroom=classroom, teacher=teacher_user, status="idle")

        url_sync = reverse('session-sync-events', kwargs={'pk': session.id})
        
        # Missing auth header
        response = api_client.post(url_sync, {'events': []}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Valid auth header
        api_client.credentials(HTTP_X_GATEWAY_AUTH='local-dev-gateway-key-secret')
        events = [
            {'event_id': 'evt_1', 'type': 'stroke', 'points': []},
            {'event_id': 'evt_2', 'type': 'bookmark', 'label': 'Test'}
        ]
        response = api_client.post(url_sync, {'events': events}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 2

        # Idempotency test (duplicate events)
        response = api_client.post(url_sync, {'events': events}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 0
