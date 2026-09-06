from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import User
from academics.models import Enrollment, StudentProfile
from common.permissions import IsStudent
from .models import Lesson, ReplayProgress
from .serializers import LessonSerializer, ReplayProgressSerializer


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides access to lessons scoped to the student's enrolled classes
    or teacher's classes.
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.role in [User.Role.ADMIN, User.Role.HEADMASTER, User.Role.TEACHER]:
            return Lesson.objects.all()

        if user.role == User.Role.STUDENT:
            class_ids = Enrollment.objects.filter(
                student__user=user,
                active=True
            ).values_list('classroom_id', flat=True)
            return Lesson.objects.filter(classroom_id__in=class_ids)

        return Lesson.objects.none()


class ReplayProgressView(APIView):
    """
    Endpoints for reading and updating an enrolled student's replay progress:
    - GET /api/v1/lessons/{id}/progress/
    - PUT /api/v1/lessons/{id}/progress/
    """
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_lesson_and_student(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        student_profile = get_object_or_404(StudentProfile, user=request.user)

        # Ensure the student is enrolled in the classroom for this lesson
        is_enrolled = Enrollment.objects.filter(
            student=student_profile,
            classroom=lesson.classroom,
            active=True
        ).exists()
        if not is_enrolled and request.user.role != User.Role.ADMIN:
            return None, None

        return lesson, student_profile

    def get(self, request, pk):
        lesson, student_profile = self.get_lesson_and_student(request, pk)
        if not lesson:
            return Response(
                {"detail": "You are not enrolled in the classroom for this lesson."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress, _ = ReplayProgress.objects.get_or_create(
            student=student_profile,
            lesson=lesson,
            defaults={'progress_percentage': 0.0, 'last_position_seconds': 0.0}
        )
        serializer = ReplayProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        lesson, student_profile = self.get_lesson_and_student(request, pk)
        if not lesson:
            return Response(
                {"detail": "You are not enrolled in the classroom for this lesson."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress, _ = ReplayProgress.objects.get_or_create(
            student=student_profile,
            lesson=lesson,
            defaults={'progress_percentage': 0.0, 'last_position_seconds': 0.0}
        )
        serializer = ReplayProgressSerializer(progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
