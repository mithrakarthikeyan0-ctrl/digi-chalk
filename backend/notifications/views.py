from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import CommunicationPreference, Notification, NotificationTemplate
from academics.models import StudentProfile, ClassRoom
from .serializers import (
    CommunicationPreferenceSerializer,
    NotificationSerializer,
    NotificationDeliveryAttemptSerializer,
    TeacherNotificationDraftSerializer
)
from .services import safe_format, dispatch_notification

class ParentCommunicationPreferenceView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommunicationPreferenceSerializer

    def get_object(self):
        # Only parents can have preferences
        if self.request.user.role != 'parent':
            return None
        pref, _ = CommunicationPreference.objects.get_or_create(parent=self.request.user.parent_profile)
        return pref

    def update(self, request, *args, **kwargs):
        if request.user.role != 'parent':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        pref = self.get_object()
        serializer = self.get_serializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Track when consent was given
        if 'consent_status' in serializer.validated_data and serializer.validated_data['consent_status']:
            serializer.validated_data['consent_captured_at'] = timezone.now()
            
        serializer.save()
        return Response(serializer.data)


class ParentNotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.role != 'parent':
            return Notification.objects.none()
        # Parents only see notifications sent to them, excluding drafts
        return Notification.objects.filter(
            recipient=self.request.user
        ).exclude(status__in=[Notification.Status.DRAFT, Notification.Status.PENDING_APPROVAL])


class TeacherNotificationDraftView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'teacher':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        drafts = Notification.objects.filter(created_by=request.user, status=Notification.Status.DRAFT)
        serializer = NotificationSerializer(drafts, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'teacher':
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = TeacherNotificationDraftSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        student_id = serializer.validated_data['student_id']
        template_key = serializer.validated_data['template_key']
        context = serializer.validated_data['context']
        
        try:
            student = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Verify teacher is assigned to student's class
        if not ClassRoom.objects.filter(enrollments__student=student, teacher=request.user).exists():
            return Response({"error": "Not assigned to this student"}, status=status.HTTP_403_FORBIDDEN)
            
        parent_link = student.parent_links.first()
        if not parent_link:
            return Response({"error": "Student has no linked parent"}, status=status.HTTP_400_BAD_REQUEST)
            
        parent = parent_link.parent
        
        try:
            pref = parent.communication_preference
            language = pref.preferred_language
            channel = [c.strip() for c in pref.allowed_channels.split(',') if c.strip()][0]
        except (AttributeError, CommunicationPreference.DoesNotExist):
            language = 'en'
            channel = 'in_app'
            
        template = NotificationTemplate.objects.filter(
            template_key=template_key, 
            language=language, 
            channel=channel,
            active=True
        ).first()
        
        if not template:
            template = NotificationTemplate.objects.filter(
                template_key=template_key, 
                language='en', 
                channel=channel,
                active=True
            ).first()
            
        if not template:
            return Response({"error": "Template not found"}, status=status.HTTP_400_BAD_REQUEST)
            
        full_context = {
            'parent_name': parent.user.full_name,
            'child_name': student.user.full_name,
            'teacher_name': request.user.full_name,
        }
        full_context.update(context)
        
        title = safe_format(template.title_template, full_context)
        body = safe_format(template.body_template, full_context)
        
        notification = Notification.objects.create(
            recipient=parent.user,
            student=student,
            template=template,
            channel=channel,
            language=language,
            title=title,
            body=body,
            status=Notification.Status.PENDING_APPROVAL if template.requires_approval else Notification.Status.QUEUED,
            created_by=request.user
        )
        
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)


class AdminPendingApprovalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.role not in ['admin', 'headmaster']:
            return Notification.objects.none()
        return Notification.objects.filter(status=Notification.Status.PENDING_APPROVAL)


class AdminNotificationActionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def _get_notification(self, pk, user):
        if user.role not in ['admin', 'headmaster']:
            return None
        try:
            return Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return None

    def post(self, request, pk, action):
        notification = self._get_notification(pk, request.user)
        if not notification:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        if action == 'approve':
            if notification.status != Notification.Status.PENDING_APPROVAL:
                return Response({"error": "Not pending approval"}, status=status.HTTP_400_BAD_REQUEST)
            notification.status = Notification.Status.APPROVED
            notification.approved_by = request.user
            notification.approved_at = timezone.now()
            notification.save()
            return Response({"status": "approved"})
            
        elif action == 'cancel':
            notification.status = Notification.Status.CANCELLED
            notification.save()
            return Response({"status": "cancelled"})
            
        elif action == 'send':
            if notification.status not in [Notification.Status.APPROVED, Notification.Status.QUEUED]:
                return Response({"error": "Must be approved or queued"}, status=status.HTTP_400_BAD_REQUEST)
            success = dispatch_notification(notification)
            return Response({"status": "sent" if success else "failed", "notification_status": notification.status})
            
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AdminDeliveryHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationDeliveryAttemptSerializer

    def get_queryset(self):
        if self.request.user.role not in ['admin', 'headmaster']:
            return NotificationDeliveryAttempt.objects.none()
        pk = self.kwargs.get('pk')
        return NotificationDeliveryAttempt.objects.filter(notification_id=pk)
