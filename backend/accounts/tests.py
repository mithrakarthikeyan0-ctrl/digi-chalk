import pytest
from rest_framework import status
from django.urls import reverse
from accounts.models import User

@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration(self, api_client):
        url = reverse('auth-register')
        data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "password123",
            "role": "student"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_user_login(self, api_client, student_user):
        url = reverse('auth-login')
        data = {
            "email": student_user.email,
            "password": "password123"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == student_user.email

    def test_me_endpoint_unauthenticated(self, api_client):
        url = reverse('auth-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_endpoint_student_profile(self, api_client, student_user, student_profile):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])
        
        url_me = reverse('auth-me')
        response = api_client.get(url_me)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == 'student'
        assert 'student_profile' in response.data
        assert response.data['student_profile']['admission_number'] == student_profile.admission_number
