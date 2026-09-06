import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestAcademicsPermissions:
    def test_student_can_view_enrolled_classes(self, api_client, student_user, enrollment, classroom):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": student_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_classes = reverse('classroom-list')
        response = api_client.get(url_classes)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(classroom.id)

    def test_parent_can_view_child_classes(self, api_client, parent_user, parent_student_link, enrollment, classroom):
        url = reverse('auth-login')
        token_response = api_client.post(url, {"email": parent_user.email, "password": "password123"})
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_response.data['access'])

        url_classes = reverse('classroom-list')
        response = api_client.get(url_classes)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(classroom.id)
