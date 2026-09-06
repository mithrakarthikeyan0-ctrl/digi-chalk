from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsTeacher, IsStudent, IsParent, IsHeadmaster
from academics.models import ClassRoom, Enrollment, ParentStudentLink
from sessions.models import ClassSession
from attendance.models import AttendanceRecord
from django.db.models import Count, Q
from attendance.services import manual_attendance_override

# ======================== TEACHER ========================
class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    def get(self, request):
        user = request.user
        recent_sessions = ClassSession.objects.filter(teacher=user).order_by('-started_at')[:5]
        return Response({
            "recent_sessions": [{"id": s.id, "status": s.status, "started_at": s.started_at, "classroom": s.classroom.name} for s in recent_sessions]
        })

class TeacherClassesView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    def get(self, request):
        # Return classes the teacher is assigned to (mock: all for now)
        classes = ClassRoom.objects.all()
        return Response([{"id": c.id, "name": c.name, "grade": c.grade_level, "section": c.section} for c in classes])

class TeacherClassAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    def get(self, request, pk):
        records = AttendanceRecord.objects.filter(class_session__classroom_id=pk).select_related('student', 'student__user')
        return Response([{
            "id": r.id, 
            "student_name": r.student.user.full_name,
            "session_id": r.class_session_id,
            "status": r.status
        } for r in records])

class TeacherAttendanceOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    def post(self, request, pk):
        new_status = request.data.get('status')
        reason = request.data.get('reason')
        if new_status not in dict(AttendanceRecord.Status.choices):
            return Response({"error": "Invalid status"}, status=400)
        
        record = manual_attendance_override(pk, request.user, new_status, reason)
        return Response({"id": record.id, "status": record.status, "reason": record.override_reason})

class TeacherSessionEngagementView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    def get(self, request, pk):
        return Response({"session_id": pk, "engagement_score": 85})

# ======================== STUDENT ========================
class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    def get(self, request):
        return Response({"summary": "Welcome to Student Dashboard"})

class StudentAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    def get(self, request):
        student = request.user.student_profile
        records = AttendanceRecord.objects.filter(student=student)
        return Response([{"id": r.id, "session": r.class_session.id, "status": r.status, "date": r.created_at} for r in records])

class StudentEngagementView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    def get(self, request):
        return Response({"score": 92})

class StudentLessonsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    def get(self, request):
        return Response([])

class StudentQuizzesView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    def get(self, request):
        return Response([])

# ======================== PARENT ========================
class ParentChildrenView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get(self, request):
        parent = request.user.parent_profile
        links = ParentStudentLink.objects.filter(parent=parent).select_related('student', 'student__user')
        return Response([{"id": l.student.id, "name": l.student.user.full_name} for l in links])

class ParentChildSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get(self, request, student_id):
        return Response({"student_id": student_id, "attendance_pct": 95, "engagement": 88})

class ParentChildAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get(self, request, student_id):
        records = AttendanceRecord.objects.filter(student_id=student_id)
        return Response([{"id": r.id, "status": r.status} for r in records])

class ParentChildLessonsView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get(self, request, student_id):
        # Enforce that parent can only see their own linked children
        parent = request.user.parent_profile
        if not ParentStudentLink.objects.filter(parent=parent, student_id=student_id).exists():
            return Response(status=403)
            
        from lessons.models import ReplayProgress
        from quizzes.models import QuizAttempt
        
        progresses = ReplayProgress.objects.filter(student_id=student_id)
        attempts = QuizAttempt.objects.filter(student_id=student_id)
        
        return Response({
            "completed_lessons": [{"lesson": p.lesson.title, "progress": p.progress_percentage} for p in progresses if p.progress_percentage >= 90],
            "completed_quizzes": [{"quiz": a.quiz.title, "score": a.score} for a in attempts if a.completed_at]
        })

# ======================== HEADMASTER ========================
class HeadmasterDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsHeadmaster]
    def get(self, request):
        from quizzes.models import QuizAttempt
        total_attempts = QuizAttempt.objects.filter(completed_at__isnull=False).count()
        return Response({"school_avg_attendance": 92, "school_avg_engagement": 85, "total_quizzes_completed": total_attempts})

class HeadmasterClassesView(APIView):
    permission_classes = [IsAuthenticated, IsHeadmaster]
    def get(self, request):
        classes = ClassRoom.objects.all()
        return Response([{"id": c.id, "name": c.name} for c in classes])

class HeadmasterAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsHeadmaster]
    def get(self, request):
        # A real implementation would aggregate by class
        return Response([{"class_name": "Class 8A", "attendance_pct": 92}])
