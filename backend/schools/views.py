from rest_framework import viewsets, permissions
from .models import School
from .serializers import SchoolSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for schools.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]
