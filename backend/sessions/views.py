from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import User
from academics.models import Enrollment, ParentStudentLink
from common.permissions import IsTeacher, IsGateway
from .models import ClassSession, Bookmark, SessionEvent
from .serializers import ClassSessionSerializer, BookmarkSerializer


class ClassSessionViewSet(viewsets.ModelViewSet):
    """
    Manages live and recorded chalkboard sessions:
    - Teacher: starts and controls sessions, adds bookmarks
    - Student: views live/past sessions for enrolled classes
    - Parent: views sessions for children's classes
    - Headmaster: views school session activity
    """
    serializer_class = ClassSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_bookmark']:
            return [permissions.IsAuthenticated(), IsTeacher()]
        if self.action == 'sync_events':
            return [IsGateway()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'sync_events':
            return ClassSession.objects.all()

        user = self.request.user
        if not user.is_authenticated:
            return ClassSession.objects.none()

        if user.role in [User.Role.ADMIN, User.Role.HEADMASTER]:
            return ClassSession.objects.all()

        if user.role == User.Role.TEACHER:
            return ClassSession.objects.filter(teacher=user)

        if user.role == User.Role.STUDENT:
            class_ids = Enrollment.objects.filter(
                student__user=user,
                active=True
            ).values_list('classroom_id', flat=True)
            return ClassSession.objects.filter(classroom_id__in=class_ids)

        if user.role == User.Role.PARENT:
            student_ids = ParentStudentLink.objects.filter(
                parent__user=user
            ).values_list('student_id', flat=True)
            class_ids = Enrollment.objects.filter(
                student_id__in=student_ids,
                active=True
            ).values_list('classroom_id', flat=True)
            return ClassSession.objects.filter(classroom_id__in=class_ids)

        return ClassSession.objects.none()

    def perform_create(self, serializer):
        status_val = self.request.data.get('status', ClassSession.Status.RECORDING)
        started_at = timezone.now() if status_val == ClassSession.Status.RECORDING else None
        serializer.save(
            teacher=self.request.user,
            status=status_val,
            started_at=started_at
        )

    @action(detail=True, methods=['post'], url_path='end', permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def end_session(self, request, pk=None):
        session = self.get_object()
        if session.teacher != request.user and request.user.role != User.Role.ADMIN:
            return Response({"detail": "You can only end your own sessions."}, status=status.HTTP_403_FORBIDDEN)
        
        session.status = ClassSession.Status.ENDED
        session.ended_at = timezone.now()
        session.save()
        return Response(self.get_serializer(session).data)

    @action(detail=True, methods=['get'], url_path='bookmarks', permission_classes=[permissions.IsAuthenticated])
    def get_bookmarks(self, request, pk=None):
        session = self.get_object()
        bookmarks = session.bookmarks.all()
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='bookmarks', permission_classes=[permissions.IsAuthenticated, IsTeacher])
    def add_bookmark(self, request, pk=None):
        session = self.get_object()
        # Verify the teacher owns this session (or is admin)
        if session.teacher != request.user and request.user.role != User.Role.ADMIN:
            return Response(
                {"detail": "You can only add bookmarks to sessions you conducted."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = BookmarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                session=session,
                created_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='sync', authentication_classes=[])
    def sync_events(self, request, pk=None):
        """
        Receives an array of events from the local Gateway and stores them.
        Uses idempotency keys (event_id) to ignore duplicates.
        """
        session = self.get_object()
        events_data = request.data.get('events', [])
        
        if not isinstance(events_data, list):
            return Response({"detail": "Expected a list of events under 'events' key."}, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        for event in events_data:
            event_id = event.get('event_id')
            event_type = event.get('type')
            
            if not event_id or not event_type:
                continue
                
            # Idempotency check
            if SessionEvent.objects.filter(event_id=event_id).exists():
                continue
                
            SessionEvent.objects.create(
                session=session,
                event_id=event_id,
                event_type=event_type,
                payload=event
            )
            created_count += 1
            
        return Response({"detail": "Sync successful", "created": created_count}, status=status.HTTP_200_OK)
