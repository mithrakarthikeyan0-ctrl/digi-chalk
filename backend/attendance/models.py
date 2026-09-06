from django.db import models
from django.conf import settings
from common.models import UUIDTimeStampedModel
from academics.models import StudentProfile
from sessions.models import ClassSession

class StudentDeviceRegistration(UUIDTimeStampedModel):
    """
    Links a hashed/minimised hardware token to a student for proximity detection.
    Does not store raw MAC addresses.
    """
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='device')
    device_token_hash = models.CharField(max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Student Device Registration'
        verbose_name_plural = 'Student Device Registrations'

    def __str__(self):
        return f"Device for {self.student.user.full_name}"

class AttendanceRecord(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PRESENT = 'present', 'Present'
        LATE = 'late', 'Late'
        ABSENT = 'absent', 'Absent'
        REJECTED = 'rejected', 'Rejected'
        
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, blank=True) # e.g. 'dual_factor', 'manual_override'
    override_reason = models.CharField(max_length=255, blank=True)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('student', 'class_session')
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.user.full_name} - {self.class_session} ({self.status})"

class AttendanceVerificationEvent(UUIDTimeStampedModel):
    """
    Raw logs of verification events (RFID scan or local gateway proximity).
    Matched to confirm attendance.
    """
    class EventType(models.TextChoices):
        RFID = 'rfid', 'RFID Scan'
        PROXIMITY = 'proximity', 'Gateway Proximity'
        
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='verification_events')
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='verification_events')
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    gateway_event_id = models.CharField(max_length=100, unique=True, null=True, blank=True) # for idempotency

    class Meta:
        verbose_name = 'Attendance Verification Event'
        verbose_name_plural = 'Attendance Verification Events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} for {self.student.user.full_name} at {self.created_at}"
