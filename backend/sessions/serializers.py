from rest_framework import serializers
from .models import ClassSession, Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'session', 'timestamp_seconds', 'label', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'session', 'created_by', 'created_by_name', 'created_at']


class ClassSessionSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    bookmarks = BookmarkSerializer(many=True, read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            'id', 'classroom', 'classroom_name', 'teacher', 'teacher_name',
            'status', 'started_at', 'ended_at', 'bookmarks', 'created_at'
        ]
        read_only_fields = ['id', 'teacher', 'teacher_name', 'classroom_name', 'created_at']
