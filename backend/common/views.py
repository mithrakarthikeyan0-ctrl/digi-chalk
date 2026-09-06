from django.db import connection
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="System Health Check",
    description="Returns service health status, timestamp, and database connectivity.",
    responses={200: dict}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Public health check endpoint to verify API and database liveness.
    """
    db_status = "connected"
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return Response({
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "digi-chalk-backend",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": timezone.now().isoformat(),
    })


@extend_schema(
    summary="System Readiness Check",
    description="Returns service readiness status (used by Kubernetes or Docker load balancers).",
    responses={200: dict}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint to verify the API is fully ready to accept traffic.
    """
    db_status = "connected"
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    if db_status != "connected":
        return Response({
            "status": "unready",
            "database": db_status
        }, status=503)

    return Response({
        "status": "ready",
        "database": db_status
    })
