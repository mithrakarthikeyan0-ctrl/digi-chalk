from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import datetime

from common.permissions import IsTeacher, IsHeadmaster
from academics.models import StudentProfile, ClassRoom
from ews.models import (
    FeatureSnapshot, ModelVersion, RiskAssessment, 
    InterventionCase, InterventionNote, NotificationDraft
)
from ews.pipeline import generate_feature_snapshot
from ews.ml.inference import run_inference
from ews.ml.training import train_baseline_model
import pandas as pd

def check_ews_access(user):
    """Only Teacher or Headmaster roles can access EWS"""
    return user.role in ['teacher', 'headmaster']

class GenerateFeatureSnapshotView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        student_id = request.data.get('student_id')
        days = request.data.get('days', 30)
        
        try:
            student = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
            
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        snapshot = generate_feature_snapshot(student, start_date, end_date)
        return Response({"snapshot_id": snapshot.id}, status=status.HTTP_201_CREATED)

class TrainModelView(APIView):
    permission_classes = [IsAuthenticated, IsHeadmaster]
    
    def post(self, request):
        version_name = request.data.get('version_name')
        use_rf = request.data.get('use_rf', False)
        
        if not version_name:
            return Response({"error": "version_name is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # In a real scenario, this would use a celery task and query real FeatureSnapshots.
        # For phase 5, we delegate to the management command logic or run it synchronously if small.
        # Since this shouldn't run in a web request, we will return an error instructing to use the CLI.
        return Response({
            "error": "Training must be run via management command to prevent request timeouts.",
            "command": f"python manage.py train_ews_model --version_name {version_name}"
        }, status=status.HTTP_400_BAD_REQUEST)

class RunAssessmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        snapshot_id = request.data.get('snapshot_id')
        
        try:
            snapshot = FeatureSnapshot.objects.get(id=snapshot_id)
        except FeatureSnapshot.DoesNotExist:
            return Response({"error": "Snapshot not found"}, status=status.HTTP_404_NOT_FOUND)
            
        active_model = ModelVersion.objects.filter(approval_status=ModelVersion.Status.ACTIVE).order_by('-activated_at').first()
        if not active_model:
            # Fallback to approved or draft for demo purposes if no active
            active_model = ModelVersion.objects.first()
            if not active_model:
                return Response({"error": "No EWS models available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        try:
            score, risk_band, top_factors = run_inference(snapshot, active_model)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        assessment = RiskAssessment.objects.create(
            student=snapshot.student,
            feature_snapshot=snapshot,
            model_version=active_model,
            score=score,
            risk_band=risk_band,
            top_contributing_factors=top_factors
        )
        
        return Response({
            "assessment_id": assessment.id,
            "risk_band": assessment.risk_band,
            "status": assessment.status
        }, status=status.HTTP_201_CREATED)

class AssessmentListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        assessments = RiskAssessment.objects.all()
        # Teacher scoping: only their students
        if request.user.role == 'teacher':
            # Simplified mock: real implementation would filter by ClassSession/Enrollment
            pass
            
        data = [{
            "id": a.id,
            "student_name": a.student.user.full_name,
            "risk_band": a.risk_band,
            "status": a.status,
            "generated_at": a.generated_at
        } for a in assessments]
        
        return Response(data)

class AssessmentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        try:
            a = RiskAssessment.objects.get(id=pk)
        except RiskAssessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "id": a.id,
            "student_name": a.student.user.full_name,
            "risk_band": a.risk_band,
            "score": a.score, # Viewable by staff only
            "top_contributing_factors": a.top_contributing_factors,
            "status": a.status,
            "generated_at": a.generated_at
        })

class ReviewAssessmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        try:
            a = RiskAssessment.objects.get(id=pk)
        except RiskAssessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        action = request.data.get('action') # 'dismiss', 'create_case'
        
        a.status = RiskAssessment.Status.REVIEWED
        a.reviewed_by = request.user
        a.reviewed_at = timezone.now()
        
        if action == 'dismiss':
            a.status = RiskAssessment.Status.DISMISSED
            a.save()
            return Response({"status": "dismissed"})
            
        elif action == 'create_case':
            a.status = RiskAssessment.Status.ACTION_PLANNED
            a.save()
            
            case = InterventionCase.objects.create(
                risk_assessment=a,
                assigned_staff=request.user
            )
            return Response({"status": "action_planned", "case_id": case.id})
            
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class InterventionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        cases = InterventionCase.objects.all()
        data = [{
            "id": c.id,
            "student": c.risk_assessment.student.user.full_name,
            "status": c.status,
            "assigned_staff": c.assigned_staff.full_name if c.assigned_staff else None
        } for c in cases]
        return Response(data)

    def post(self, request):
        # Create directly if needed, usually done via ReviewAssessmentView
        pass

class InterventionNoteCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        try:
            case = InterventionCase.objects.get(id=pk)
        except InterventionCase.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        content = request.data.get('content')
        note = InterventionNote.objects.create(
            intervention_case=case,
            author=request.user,
            content=content
        )
        return Response({"id": note.id}, status=status.HTTP_201_CREATED)

class NotificationDraftCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not check_ews_access(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        case_id = request.data.get('case_id')
        try:
            case = InterventionCase.objects.get(id=case_id)
        except InterventionCase.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        draft = NotificationDraft.objects.create(
            intervention_case=case,
            recipient_type=request.data.get('recipient_type', 'parent'),
            content=request.data.get('content')
        )
        return Response({"id": draft.id}, status=status.HTTP_201_CREATED)

class ApproveNotificationDraftView(APIView):
    permission_classes = [IsAuthenticated, IsHeadmaster] # Higher privilege for approval
    
    def post(self, request, pk):
        try:
            draft = NotificationDraft.objects.get(id=pk)
        except NotificationDraft.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        draft.status = NotificationDraft.Status.APPROVED
        draft.approved_by = request.user
        draft.approved_at = timezone.now()
        draft.save()
        
        # Real send logic deferred to Phase 6.
        return Response({"status": "approved", "detail": "Deferred actual delivery to phase 6."})
