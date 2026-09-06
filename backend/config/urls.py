from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from common.views import health_check, readiness_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health Check
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/readiness/', readiness_check, name='readiness-check'),

    # Application endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/schools/', include('schools.urls')),
    path('api/v1/classes/', include('academics.urls')),
    path('api/v1/sessions/', include('sessions.urls')),
    path('api/v1/lessons/', include('lessons.urls')),
    path('api/v1/', include('quizzes.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/gateway/', include('attendance.urls')),
    path('api/v1/', include('dashboards.urls')),
    path('api/v1/ews/', include('ews.urls')),
    path('api/v1/', include('notifications.urls')),

    # OpenAPI 3 / Swagger Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
