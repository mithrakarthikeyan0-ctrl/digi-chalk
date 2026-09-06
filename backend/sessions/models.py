from django.db import models
from django.conf import settings
from common.models import UUIDTimeStampedModel


class ClassSession(UUIDTimeStampedModel):
    """
    Represents a live or recorded classroom session broadcasting chalk notes.
    """
    class Status(models.TextChoices):
        IDLE = 'idle', 'Idle'
        RECORDING = 'recording', 'Recording'
        ENDED = 'ended', 'Ended'

    classroom = models.ForeignKey(
        'academics.ClassRoom',
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conducted_sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE,
        db_index=True
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Class Session'
        verbose_name_plural = 'Class Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session: {self.classroom.name} ({self.get_status_display()}) by {self.teacher.full_name}"


class Bookmark(UUIDTimeStampedModel):
    """
    Marker placed by the teacher during a session to highlight key moments.
    """
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    timestamp_seconds = models.FloatField()
    label = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_bookmarks'
    )

    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        ordering = ['timestamp_seconds']

    def __str__(self):
        return f"Bookmark at {self.timestamp_seconds}s: {self.label} ({self.session.id})"


class SessionEvent(UUIDTimeStampedModel):
    """
    Offline sync storage for strokes and other live board events from the Gateway.
    """
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()

    class Meta:
        verbose_name = 'Session Event'
        verbose_name_plural = 'Session Events'
        ordering = ['created_at']

    def __str__(self):
        return f"Event {self.event_type} ({self.event_id}) for {self.session.id}"
