from django.db import models
from common.models import UUIDTimeStampedModel


class Lesson(UUIDTimeStampedModel):
    """
    Represents an archival or curriculum lesson corresponding to chalkboard notes.
    """
    classroom = models.ForeignKey(
        'academics.ClassRoom',
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_seconds = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.classroom.name})"


class ReplayProgress(UUIDTimeStampedModel):
    """
    Tracks an individual student's playhead position and completion percentage
    for an asynchronous whiteboard replay.
    """
    student = models.ForeignKey(
        'academics.StudentProfile',
        on_delete=models.CASCADE,
        related_name='replay_progresses'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='student_progresses'
    )
    progress_percentage = models.FloatField(default=0.0)
    last_position_seconds = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('student', 'lesson')
        verbose_name = 'Replay Progress'
        verbose_name_plural = 'Replay Progresses'

    def __str__(self):
        return f"{self.student.user.full_name} on {self.lesson.title}: {self.progress_percentage}%"

class LessonAsset(UUIDTimeStampedModel):
    class AssetType(models.TextChoices):
        RECORDING = 'recording', 'Recording'
        RECAP = 'recap', 'Recap'
        DOCUMENT = 'document', 'Document'
        AUDIO = 'audio', 'Audio'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    title = models.CharField(max_length=255)
    media_url = models.URLField(max_length=1000)
    low_bandwidth_url = models.URLField(max_length=1000, blank=True)
    duration_seconds = models.IntegerField(default=0)
    language = models.CharField(max_length=10, default='en')
    is_active = models.BooleanField(default=True)

class LessonBookmark(UUIDTimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=255)
    timestamp_seconds = models.IntegerField(default=0)

class LessonAccessAssignment(UUIDTimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey('academics.StudentProfile', on_delete=models.CASCADE, related_name='lesson_assignments')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lesson', 'student')
