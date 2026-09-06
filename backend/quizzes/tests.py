import pytest
from rest_framework import status
from django.urls import reverse
from quizzes.models import Quiz, QuizQuestion, QuizChoice, QuizAttempt

@pytest.mark.django_db
class TestQuizzes:
    def test_quiz_attempt_flow(self, api_client, student_user, student_profile, classroom, enrollment):
        from lessons.models import Lesson
        lesson = Lesson.objects.create(classroom=classroom, title="Math 101", published_at="2025-01-01T00:00:00Z")
        quiz = Quiz.objects.create(lesson=lesson, title="Fractions", is_published=True, allow_retry=False)
        q1 = QuizQuestion.objects.create(quiz=quiz, text="1+1?", order=1)
        c1_1 = QuizChoice.objects.create(question=q1, text="2", is_correct=True)
        c1_2 = QuizChoice.objects.create(question=q1, text="3", is_correct=False)
        
        token = api_client.post(reverse('auth-login'), {"email": student_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url_start = reverse('student-quiz-attempt-create', kwargs={'pk': quiz.id})
        res = api_client.post(url_start)
        assert res.status_code == status.HTTP_201_CREATED
        attempt_id = res.data['attempt_id']
        
        url_detail = reverse('student-quiz-detail', kwargs={'pk': quiz.id})
        res = api_client.get(url_detail)
        assert 'is_correct' not in res.data['questions'][0]['choices'][0]
        
        url_submit = reverse('student-quiz-attempt-submit', kwargs={'pk': attempt_id})
        res = api_client.post(url_submit, {"answers": [{"question_id": str(q1.id), "choice_id": str(c1_1.id)}]}, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['score'] == 100.0
        
        res = api_client.post(url_start)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
