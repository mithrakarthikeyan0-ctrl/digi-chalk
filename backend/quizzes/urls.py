from django.urls import path
from . import views

urlpatterns = [
    path('student/quizzes/', views.StudentQuizListView.as_view(), name='student-quiz-list'),
    path('student/quizzes/<uuid:pk>/', views.StudentQuizDetailView.as_view(), name='student-quiz-detail'),
    path('student/quizzes/<uuid:pk>/attempts/', views.StudentQuizAttemptCreateView.as_view(), name='student-quiz-attempt-create'),
    path('student/quiz-attempts/<uuid:pk>/', views.StudentQuizAttemptDetailView.as_view(), name='student-quiz-attempt-detail'),
    path('student/quiz-attempts/<uuid:pk>/submit/', views.StudentQuizAttemptSubmitView.as_view(), name='student-quiz-attempt-submit'),
]
