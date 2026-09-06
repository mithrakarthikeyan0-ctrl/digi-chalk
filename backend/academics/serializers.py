from rest_framework import serializers
from .models import ClassRoom, StudentProfile, ParentProfile, ParentStudentLink, Enrollment


class ClassRoomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = ClassRoom
        fields = ['id', 'school', 'school_name', 'name', 'grade_level', 'section', 'created_at']
        read_only_fields = ['id', 'school_name', 'created_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'full_name', 'email', 'school', 'admission_number']
        read_only_fields = ['id', 'full_name', 'email']


class EnrollmentSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'classroom', 'classroom_name', 'academic_year', 'active']
        read_only_fields = ['id', 'classroom_name', 'student_name']
