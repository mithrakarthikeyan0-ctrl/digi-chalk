import pytest
from rest_framework import status
from django.urls import reverse
from lessons.models import Lesson, ReplayProgress

@pytest.mark.django_db
class TestLessons:
    def test_lesson_access(self, api_client, student_user, classroom, enrollment):
        lesson = Lesson.objects.create(classroom=classroom, title="Math 101", published_at="2025-01-01T00:00:00Z")
        
        token = api_client.post(reverse('auth-login'), {"email": student_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Student should see the lesson since they are enrolled in the classroom
        url = reverse('lesson-list')
        res = api_client.get(url)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['results']) == 1
        
    def test_replay_progress(self, api_client, student_user, student_profile, classroom, enrollment):
        lesson = Lesson.objects.create(classroom=classroom, title="Math 101", published_at="2025-01-01T00:00:00Z")
        
        token = api_client.post(reverse('auth-login'), {"email": student_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url = reverse('lesson-progress', kwargs={'pk': lesson.id})
        res = api_client.put(url, {"progress_percentage": 50.0, "last_position_seconds": 120.0})
        assert res.status_code == status.HTTP_200_OK
        
        prog = ReplayProgress.objects.get(student=student_profile, lesson=lesson)
        assert prog.progress_percentage == 50.0
