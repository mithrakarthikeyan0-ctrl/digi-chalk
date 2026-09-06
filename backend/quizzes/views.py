from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Quiz, QuizQuestion, QuizChoice, QuizAttempt, QuizAnswer
from .serializers import QuizSerializer, QuizAttemptSerializer
from common.permissions import IsTeacher
from academics.models import ClassRoom

class StudentQuizListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        student = request.user.student_profile
        classrooms = ClassRoom.objects.filter(enrollments__student=student)
        quizzes = Quiz.objects.filter(lesson__classroom__in=classrooms, is_published=True)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

class StudentQuizDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if request.user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        student = request.user.student_profile
        try:
            quiz = Quiz.objects.get(id=pk, lesson__classroom__in=ClassRoom.objects.filter(enrollments__student=student), is_published=True)
        except Quiz.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

class StudentQuizAttemptCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if request.user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        student = request.user.student_profile
        try:
            quiz = Quiz.objects.get(id=pk, lesson__classroom__in=ClassRoom.objects.filter(enrollments__student=student), is_published=True)
        except Quiz.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        existing_attempt = QuizAttempt.objects.filter(quiz=quiz, student=student).order_by('-started_at').first()
        if existing_attempt:
            if existing_attempt.completed_at and not quiz.allow_retry:
                return Response({"error": "You have already completed this quiz and retries are not allowed."}, status=status.HTTP_400_BAD_REQUEST)
            elif not existing_attempt.completed_at:
                return Response({"attempt_id": existing_attempt.id})
                
        attempt = QuizAttempt.objects.create(quiz=quiz, student=student)
        return Response({"attempt_id": attempt.id}, status=status.HTTP_201_CREATED)

class StudentQuizAttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if request.user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        try:
            attempt = QuizAttempt.objects.get(id=pk, student=request.user.student_profile)
        except QuizAttempt.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)

class StudentQuizAttemptSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if request.user.role != 'student':
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        try:
            attempt = QuizAttempt.objects.get(id=pk, student=request.user.student_profile)
        except QuizAttempt.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        if attempt.completed_at:
            return Response({"error": "This attempt is already completed."}, status=status.HTTP_400_BAD_REQUEST)
            
        answers_data = request.data.get('answers', [])
        
        correct_count = 0
        total_questions = attempt.quiz.questions.count()
        
        for ans in answers_data:
            try:
                question = QuizQuestion.objects.get(id=ans['question_id'], quiz=attempt.quiz)
                choice = QuizChoice.objects.get(id=ans['choice_id'], question=question)
                
                QuizAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_choice': choice}
                )
                
                if choice.is_correct:
                    correct_count += 1
            except (QuizQuestion.DoesNotExist, QuizChoice.DoesNotExist):
                continue
                
        attempt.completed_at = timezone.now()
        attempt.score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        attempt.save()
        
        return Response({"score": attempt.score, "total_questions": total_questions, "correct_count": correct_count})
