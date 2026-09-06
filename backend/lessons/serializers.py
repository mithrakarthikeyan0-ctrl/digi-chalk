from rest_framework import serializers
from .models import Lesson, ReplayProgress, LessonAsset, LessonBookmark

class LessonAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAsset
        fields = ['id', 'asset_type', 'title', 'media_url', 'low_bandwidth_url', 'duration_seconds', 'language', 'is_active']

class LessonBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBookmark
        fields = ['id', 'title', 'timestamp_seconds']

class LessonSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    assets = LessonAssetSerializer(many=True, read_only=True)
    bookmarks = LessonBookmarkSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'classroom', 'classroom_name', 'title',
            'description', 'duration_seconds', 'published_at', 'created_at',
            'assets', 'bookmarks'
        ]
        read_only_fields = ['id', 'classroom_name', 'created_at']


class ReplayProgressSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = ReplayProgress
        fields = [
            'id', 'student', 'student_name', 'lesson', 'lesson_title',
            'progress_percentage', 'last_position_seconds', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'student_name', 'lesson', 'lesson_title', 'updated_at']

    def validate_progress_percentage(self, value):
        if value < 0.0 or value > 100.0:
            raise serializers.ValidationError("Progress percentage must be between 0.0 and 100.0.")
        return value

    def validate_last_position_seconds(self, value):
        if value < 0.0:
            raise serializers.ValidationError("Last position seconds cannot be negative.")
        return value
