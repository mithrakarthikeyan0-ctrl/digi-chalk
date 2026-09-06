from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassSessionViewSet

router = DefaultRouter()
router.register(r'', ClassSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
