from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import LearningEventSerializer
from common.permissions import IsStudent
from lessons.models import Lesson

class StudentEventCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        serializer = LearningEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user.student_profile, lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
