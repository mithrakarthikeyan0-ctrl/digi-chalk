from django.urls import path
from . import views

urlpatterns = [
    # Teacher APIs
    path('teacher/dashboard/', views.TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher/classes/', views.TeacherClassesView.as_view(), name='teacher-classes'),
    path('teacher/classes/<uuid:pk>/attendance/', views.TeacherClassAttendanceView.as_view(), name='teacher-class-attendance'),
    path('teacher/attendance/<uuid:pk>/override/', views.TeacherAttendanceOverrideView.as_view(), name='teacher-attendance-override'),
    path('teacher/sessions/<uuid:pk>/engagement/', views.TeacherSessionEngagementView.as_view(), name='teacher-session-engagement'),

    # Student APIs
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student-dashboard'),
    path('student/attendance/', views.StudentAttendanceView.as_view(), name='student-attendance'),
    path('student/engagement/', views.StudentEngagementView.as_view(), name='student-engagement'),
    path('student/lessons/', views.StudentLessonsView.as_view(), name='student-lessons'),
    path('student/quizzes/available/', views.StudentQuizzesView.as_view(), name='student-quizzes'),

    # Parent APIs
    path('parent/children/', views.ParentChildrenView.as_view(), name='parent-children'),
    path('parent/children/<uuid:student_id>/summary/', views.ParentChildSummaryView.as_view(), name='parent-child-summary'),
    path('parent/children/<uuid:student_id>/attendance/', views.ParentChildAttendanceView.as_view(), name='parent-child-attendance'),
    path('parent/children/<uuid:student_id>/lessons/', views.ParentChildLessonsView.as_view(), name='parent-child-lessons'),

    # Headmaster APIs
    path('headmaster/dashboard/', views.HeadmasterDashboardView.as_view(), name='headmaster-dashboard'),
    path('headmaster/classes/', views.HeadmasterClassesView.as_view(), name='headmaster-classes'),
    path('headmaster/attendance-summary/', views.HeadmasterAttendanceSummaryView.as_view(), name='headmaster-attendance-summary'),
]
