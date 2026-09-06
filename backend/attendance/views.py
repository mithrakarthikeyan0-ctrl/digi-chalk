from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from common.permissions import IsGateway
from .serializers import GatewayAttendanceEventSerializer
from .services import process_attendance_event
from sessions.models import ClassSession
from academics.models import StudentProfile
from .models import StudentDeviceRegistration

@api_view(['POST'])
@authentication_classes([]) # Gateway auth bypassed standard JWT
@permission_classes([IsGateway])
def gateway_attendance_ingest(request):
    """
    Ingests RFID and Proximity events from the classroom Gateway.
    Idempotent endpoint.
    """
    events_data = request.data.get('events', [])
    serializer = GatewayAttendanceEventSerializer(data=events_data, many=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    processed_count = 0
    for event_data in serializer.validated_data:
        try:
            session = ClassSession.objects.get(id=event_data['session_id'])
            
            student = None
            if event_data['event_type'] == 'rfid':
                student = StudentProfile.objects.get(id=event_data['student_id'])
            elif event_data['event_type'] == 'proximity':
                device = StudentDeviceRegistration.objects.get(device_token_hash=event_data['device_token_hash'], is_active=True)
                student = device.student
                
            if student:
                result = process_attendance_event(
                    student=student,
                    class_session=session,
                    event_type=event_data['event_type'],
                    gateway_event_id=event_data['event_id']
                )
                if result is not None:
                    processed_count += 1
                
        except (ClassSession.DoesNotExist, StudentProfile.DoesNotExist, StudentDeviceRegistration.DoesNotExist):
            # Ignore invalid references from gateway, or log them
            continue

    return Response({"detail": "Sync successful", "processed": processed_count}, status=status.HTTP_200_OK)
