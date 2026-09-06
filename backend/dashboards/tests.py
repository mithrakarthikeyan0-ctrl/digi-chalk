import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestDashboardPermissions:
    def test_student_cannot_access_teacher_dashboard(self, api_client, student_user):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])
        
        res = api_client.get(reverse('teacher-dashboard'))
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_can_access_teacher_dashboard(self, api_client, teacher_user):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": teacher_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])
        
        res = api_client.get(reverse('teacher-dashboard'))
        assert res.status_code == status.HTTP_200_OK

    def test_parent_cannot_access_headmaster_dashboard(self, api_client, parent_user):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": parent_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])
        
        res = api_client.get(reverse('headmaster-dashboard'))
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_headmaster_can_access_headmaster_dashboard(self, api_client, headmaster_user):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": headmaster_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])
        
        res = api_client.get(reverse('headmaster-dashboard'))
        assert res.status_code == status.HTTP_200_OK
