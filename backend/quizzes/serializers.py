from rest_framework import serializers
from .models import Quiz, QuizQuestion, QuizChoice, QuizAttempt, QuizAnswer

class QuizChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ['id', 'text', 'order'] # Exclude is_correct

class QuizQuestionSerializer(serializers.ModelSerializer):
    choices = QuizChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'text', 'order', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'is_published', 'allow_retry', 'questions']

class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['question', 'selected_choice']

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'started_at', 'completed_at', 'score', 'answers']
        read_only_fields = ['id', 'student', 'started_at', 'completed_at', 'score']
