from django.utils import timezone
from datetime import timedelta
from ews.models import FeatureSnapshot
from attendance.models import AttendanceRecord
from analytics.models import EngagementMetric

def generate_feature_snapshot(student, start_date, end_date):
    """
    Generates a privacy-safe FeatureSnapshot for a student within a time period.
    """
    # 1. Attendance Metrics
    records = AttendanceRecord.objects.filter(
        student=student,
        created_at__range=(start_date, end_date)
    )
    total_sessions = records.count()
    present_count = records.filter(status=AttendanceRecord.Status.PRESENT).count()
    late_count = records.filter(status=AttendanceRecord.Status.LATE).count()
    
    attendance_rate = (present_count / total_sessions * 100) if total_sessions > 0 else 0.0

    # 2. Engagement Metrics (Averaging over the period)
    metrics = EngagementMetric.objects.filter(
        student=student,
        created_at__range=(start_date, end_date)
    )
    
    total_metrics = metrics.count()
    recent_engagement_score = sum(m.score for m in metrics) / total_metrics if total_metrics > 0 else 0.0
    session_participation_count = sum(m.participation_count for m in metrics)
    
    # 3. Lesson/Quiz (Mocked as 0 for this phase since detailed models aren't fully populated)
    lesson_replay_completion = 0.0
    quiz_score_avg = 0.0
    
    # 4. Trend vs Previous
    previous_start = start_date - (end_date - start_date)
    previous_metrics = EngagementMetric.objects.filter(
        student=student,
        created_at__range=(previous_start, start_date)
    )
    prev_total = previous_metrics.count()
    prev_score = sum(m.score for m in previous_metrics) / prev_total if prev_total > 0 else 0.0
    trend_vs_previous = recent_engagement_score - prev_score

    snapshot = FeatureSnapshot.objects.create(
        student=student,
        snapshot_period_start=start_date,
        snapshot_period_end=end_date,
        attendance_rate=attendance_rate,
        late_attendance_count=late_count,
        lesson_replay_completion=lesson_replay_completion,
        quiz_score_avg=quiz_score_avg,
        recent_engagement_score=recent_engagement_score,
        session_participation_count=session_participation_count,
        trend_vs_previous=trend_vs_previous,
        feature_schema_version='v1.0'
    )
    return snapshot
