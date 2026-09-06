from django.db import models
from common.models import UUIDTimeStampedModel
from academics.models import StudentProfile, ClassRoom

class EngagementMetric(UUIDTimeStampedModel):
    """
    Stores point-in-time engagement scores for students per class.
    Calculated via background tasks based on attendance, bookmarks, and replay interactions.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='engagement_metrics')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='engagement_metrics')
    
    score = models.IntegerField(help_text="Engagement score out of 100")
    attendance_rate = models.FloatField(help_text="Percentage of attended sessions")
    participation_count = models.IntegerField(default=0, help_text="Number of in-class interactions")
    calculation_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Engagement Metric'
        verbose_name_plural = 'Engagement Metrics'
        ordering = ['-calculation_timestamp']

    def __str__(self):
        return f"{self.student.user.full_name} in {self.classroom.name}: {self.score}"

class LearningEvent(UUIDTimeStampedModel):
    student = models.ForeignKey('academics.StudentProfile', on_delete=models.CASCADE, related_name='learning_events')
    lesson = models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, null=True, blank=True, related_name='learning_events')
    event_type = models.CharField(max_length=50) # e.g. lesson_opened, replay_started
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.student.user.full_name} - {self.event_type}"
