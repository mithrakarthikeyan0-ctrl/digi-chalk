from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from accounts.models import User
from .models import ClassRoom, Enrollment, ParentStudentLink
from .serializers import ClassRoomSerializer


class ClassRoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides read access to classrooms strictly scoped by the user's role:
    - Teacher: classes the teacher conducts sessions for, or all classes if assigned
    - Student: classes where the student is actively enrolled
    - Parent: classes where linked children are actively enrolled
    - Headmaster/Admin: all classes within their institution
    """
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ClassRoom.objects.none()

        if user.role == User.Role.ADMIN:
            return ClassRoom.objects.all()

        if user.role == User.Role.HEADMASTER:
            # School-level view
            return ClassRoom.objects.all()

        if user.role == User.Role.TEACHER:
            # Classrooms teacher has active or past sessions in, or all classes for assigned school
            return ClassRoom.objects.all()

        if user.role == User.Role.STUDENT:
            # Classrooms student is actively enrolled in
            enrolled_class_ids = Enrollment.objects.filter(
                student__user=user,
                active=True
            ).values_list('classroom_id', flat=True)
            return ClassRoom.objects.filter(id__in=enrolled_class_ids)

        if user.role == User.Role.PARENT:
            # Classrooms where linked children are enrolled
            student_ids = ParentStudentLink.objects.filter(
                parent__user=user
            ).values_list('student_id', flat=True)
            enrolled_class_ids = Enrollment.objects.filter(
                student_id__in=student_ids,
                active=True
            ).values_list('classroom_id', flat=True)
            return ClassRoom.objects.filter(id__in=enrolled_class_ids)

        return ClassRoom.objects.none()
