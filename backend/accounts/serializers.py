from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Public read serializer for User."""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for initial bootstrap registration."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'full_name', 'role']
        read_only_fields = ['id']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enriches JWT response payload with user metadata so frontends
    receive user id, role, and display name directly upon login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
        }
        return data
