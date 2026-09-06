import pytest
from rest_framework import status
from django.urls import reverse
from ews.models import RiskAssessment, ModelVersion, FeatureSnapshot, InterventionCase

@pytest.mark.django_db
class TestEWS:
    def test_ews_access_restrictions(self, api_client, student_user, parent_user, teacher_user):
        url = reverse('ews-assessment-list')
        
        # Student cannot access
        token = api_client.post(reverse('auth-login'), {"email": student_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        assert api_client.get(url).status_code == status.HTTP_403_FORBIDDEN
        
        # Parent cannot access
        token = api_client.post(reverse('auth-login'), {"email": parent_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        assert api_client.get(url).status_code == status.HTTP_403_FORBIDDEN
        
        # Teacher can access
        token = api_client.post(reverse('auth-login'), {"email": teacher_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        assert api_client.get(url).status_code == status.HTTP_200_OK

    def test_assessment_review_workflow(self, api_client, teacher_user, student_profile):
        token = api_client.post(reverse('auth-login'), {"email": teacher_user.email, "password": "password123"}).data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        model = ModelVersion.objects.create(version_name="test_v1", algorithm="LR", training_metrics={})
        snapshot = FeatureSnapshot.objects.create(
            student=student_profile, snapshot_period_start='2025-01-01T00:00:00Z', snapshot_period_end='2025-02-01T00:00:00Z',
            attendance_rate=90, late_attendance_count=1
        )
        assessment = RiskAssessment.objects.create(
            student=student_profile, feature_snapshot=snapshot, model_version=model,
            score=80.0, risk_band='priority', top_contributing_factors=[]
        )
        
        # Starts pending
        assert assessment.status == RiskAssessment.Status.PENDING_REVIEW
        
        # Review: create case
        url = reverse('ews-assessment-review', kwargs={'pk': assessment.id})
        res = api_client.post(url, {"action": "create_case"})
        assert res.status_code == status.HTTP_200_OK
        
        assessment.refresh_from_db()
        assert assessment.status == RiskAssessment.Status.ACTION_PLANNED
        
        case = InterventionCase.objects.get(risk_assessment=assessment)
        assert case.assigned_staff == teacher_user
