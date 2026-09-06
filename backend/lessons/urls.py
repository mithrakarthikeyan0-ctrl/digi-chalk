from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, ReplayProgressView

router = DefaultRouter()
router.register(r'', LessonViewSet, basename='lesson')

urlpatterns = [
    path('<uuid:pk>/progress/', ReplayProgressView.as_view(), name='lesson-progress'),
    path('', include(router.urls)),
]
