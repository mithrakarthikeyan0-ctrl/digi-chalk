from django.urls import path
from .views import gateway_attendance_ingest

urlpatterns = [
    path('attendance-events/', gateway_attendance_ingest, name='gateway-attendance-events'),
]
