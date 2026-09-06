from rest_framework import serializers
from .models import LearningEvent

class LearningEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningEvent
        fields = ['event_type', 'metadata', 'timestamp']
