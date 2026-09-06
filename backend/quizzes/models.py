from django.db import models
from common.models import UUIDTimeStampedModel

class Quiz(UUIDTimeStampedModel):
    lesson = models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    allow_retry = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Quiz: {self.title}"

class QuizQuestion(UUIDTimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order} for {self.quiz.title}"

class QuizChoice(UUIDTimeStampedModel):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class QuizAttempt(UUIDTimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('academics.StudentProfile', on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('quiz', 'student', 'started_at')

class QuizAnswer(UUIDTimeStampedModel):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(QuizChoice, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('attempt', 'question')
