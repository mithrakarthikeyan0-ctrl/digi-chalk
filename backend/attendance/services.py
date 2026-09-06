from django.utils import timezone
from datetime import timedelta
from .models import AttendanceRecord, AttendanceVerificationEvent, StudentDeviceRegistration

def process_attendance_event(student, class_session, event_type, gateway_event_id=None):
    """
    Records an attendance verification event and checks if dual-layer criteria are met.
    """
    # Idempotency check
    if gateway_event_id and AttendanceVerificationEvent.objects.filter(gateway_event_id=gateway_event_id).exists():
        return

    # Create the event log
    AttendanceVerificationEvent.objects.create(
        student=student,
        class_session=class_session,
        event_type=event_type,
        gateway_event_id=gateway_event_id
    )

    # Get or create pending attendance record
    record, created = AttendanceRecord.objects.get_or_create(
        student=student,
        class_session=class_session,
        defaults={'status': AttendanceRecord.Status.PENDING}
    )

    if record.status in [AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.REJECTED]:
        # Already resolved
        return record

    # Check for dual-layer within the last 5 minutes
    five_mins_ago = timezone.now() - timedelta(minutes=5)
    recent_events = AttendanceVerificationEvent.objects.filter(
        student=student,
        class_session=class_session,
        created_at__gte=five_mins_ago
    ).values_list('event_type', flat=True)

    has_rfid = AttendanceVerificationEvent.EventType.RFID in recent_events
    has_prox = AttendanceVerificationEvent.EventType.PROXIMITY in recent_events

    if has_rfid and has_prox:
        record.status = AttendanceRecord.Status.PRESENT
        record.verified_at = timezone.now()
        record.verification_method = 'dual_factor'
        record.save()

    return record

def manual_attendance_override(record_id, user, new_status, reason):
    """
    Allows a teacher to manually override an attendance status.
    """
    record = AttendanceRecord.objects.get(id=record_id)
    record.status = new_status
    record.override_reason = reason
    record.overridden_by = user
    record.verified_at = timezone.now()
    record.verification_method = 'manual_override'
    record.save()
    return record
