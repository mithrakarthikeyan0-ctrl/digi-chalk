from django.db import models
from django.conf import settings
from common.models import UUIDTimeStampedModel
from academics.models import StudentProfile

class FeatureSnapshot(UUIDTimeStampedModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='feature_snapshots')
    snapshot_period_start = models.DateTimeField()
    snapshot_period_end = models.DateTimeField()
    
    # Features (No sensitive PII like names, email, raw MACs, religion, caste)
    attendance_rate = models.FloatField()
    late_attendance_count = models.IntegerField()
    lesson_replay_completion = models.FloatField(default=0.0)
    quiz_score_avg = models.FloatField(default=0.0)
    recent_engagement_score = models.FloatField(default=0.0)
    session_participation_count = models.IntegerField(default=0)
    trend_vs_previous = models.FloatField(default=0.0) # Delta vs previous period
    
    feature_schema_version = models.CharField(max_length=50, default='v1.0')

    class Meta:
        verbose_name = 'Feature Snapshot'
        verbose_name_plural = 'Feature Snapshots'

    def __str__(self):
        return f"Snapshot for {self.student.user.full_name} ({self.snapshot_period_end.date()})"


class ModelVersion(UUIDTimeStampedModel):
    version_name = models.CharField(max_length=100, unique=True)
    algorithm = models.CharField(max_length=100) # e.g. 'LogisticRegression', 'RandomForest'
    training_data_description = models.TextField()
    feature_schema_version = models.CharField(max_length=50)
    training_metrics = models.JSONField() # JSON containing accuracy, precision, recall, etc.
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft / Evaluating'
        APPROVED = 'approved', 'Approved'
        ACTIVE = 'active', 'Active'
        DEPRECATED = 'deprecated', 'Deprecated'

    approval_status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    activated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trained_models')

    class Meta:
        verbose_name = 'Model Version'
        verbose_name_plural = 'Model Versions'

    def __str__(self):
        return f"{self.version_name} ({self.approval_status})"


class RiskAssessment(UUIDTimeStampedModel):
    class RiskBand(models.TextChoices):
        ROUTINE = 'routine', 'Routine'
        REVIEW = 'review', 'Review'
        PRIORITY = 'priority', 'Priority'
        
    class Status(models.TextChoices):
        PENDING_REVIEW = 'pending_review', 'Pending Review'
        REVIEWED = 'reviewed', 'Reviewed'
        DISMISSED = 'dismissed', 'Dismissed'
        ACTION_PLANNED = 'action_planned', 'Action Planned'

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='risk_assessments')
    feature_snapshot = models.ForeignKey(FeatureSnapshot, on_delete=models.CASCADE)
    model_version = models.ForeignKey(ModelVersion, on_delete=models.CASCADE)
    
    score = models.FloatField(help_text="Risk score from 0 to 100")
    risk_band = models.CharField(max_length=20, choices=RiskBand.choices)
    top_contributing_factors = models.JSONField(help_text="Key features driving the score")
    model_confidence = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_REVIEW)
    generated_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_assessments')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Risk Assessment'
        verbose_name_plural = 'Risk Assessments'

    def __str__(self):
        return f"{self.student.user.full_name} - {self.risk_band} ({self.status})"


class InterventionCase(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'

    risk_assessment = models.OneToOneField(RiskAssessment, on_delete=models.CASCADE, related_name='intervention_case')
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_cases')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    action_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Intervention Case'
        verbose_name_plural = 'Intervention Cases'

    def __str__(self):
        return f"Case for {self.risk_assessment.student.user.full_name} ({self.status})"


class InterventionNote(UUIDTimeStampedModel):
    intervention_case = models.ForeignKey(InterventionCase, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()

    class Meta:
        verbose_name = 'Intervention Note'
        verbose_name_plural = 'Intervention Notes'
        ordering = ['created_at']

    def __str__(self):
        return f"Note by {self.author.full_name if self.author else 'System'}"


class NotificationDraft(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        APPROVED = 'approved', 'Approved'
        CANCELLED = 'cancelled', 'Cancelled'

    intervention_case = models.ForeignKey(InterventionCase, on_delete=models.CASCADE, related_name='notification_drafts')
    recipient_type = models.CharField(max_length=50) # 'parent', 'student'
    language = models.CharField(max_length=10, default='en')
    content = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_drafts')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Notification Draft'
        verbose_name_plural = 'Notification Drafts'

    def __str__(self):
        return f"Draft for {self.intervention_case} ({self.status})"
