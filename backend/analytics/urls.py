from django.urls import path
from . import views

urlpatterns = [
    path('student/lessons/<uuid:lesson_id>/events/', views.StudentEventCreateView.as_view(), name='student-lesson-event-create'),
]
