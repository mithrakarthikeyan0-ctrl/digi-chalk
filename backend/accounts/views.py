from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT access and refresh token pair with user profile info."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Bootstrap user registration endpoint for local development and admin onboarding.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """
    Returns authenticated user's profile and role-specific details.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data

        # Enrich with role-specific profile details if present
        if request.user.role == User.Role.STUDENT and hasattr(request.user, 'student_profile'):
            profile = request.user.student_profile
            data['student_profile'] = {
                'id': str(profile.id),
                'school_id': str(profile.school_id) if profile.school_id else None,
                'admission_number': profile.admission_number,
            }
        elif request.user.role == User.Role.PARENT and hasattr(request.user, 'parent_profile'):
            profile = request.user.parent_profile
            data['parent_profile'] = {
                'id': str(profile.id),
                'school_id': str(profile.school_id) if profile.school_id else None,
            }

        return Response(data, status=status.HTTP_200_OK)
