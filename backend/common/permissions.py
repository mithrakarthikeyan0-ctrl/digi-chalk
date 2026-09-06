from django.conf import settings
from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """Allows access only to authenticated teachers."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['teacher', 'admin']
        )


class IsStudent(permissions.BasePermission):
    """Allows access only to authenticated students."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['student', 'admin']
        )


class IsParent(permissions.BasePermission):
    """Allows access only to authenticated parents."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['parent', 'admin']
        )


class IsHeadmaster(permissions.BasePermission):
    """Allows access only to authenticated headmasters or school administrators."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['headmaster', 'admin']
        )


class IsAdminRole(permissions.BasePermission):
    """Allows access only to admin role or staff users."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'admin' or request.user.is_staff or request.user.is_superuser)
        )


class IsSessionTeacherOrReadOnly(permissions.BasePermission):
    """Allows teachers who own the session to modify it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            (obj.teacher == request.user or request.user.role == 'admin')
        )


class IsGateway(permissions.BasePermission):
    """Allows access only if the correct GATEWAY_API_KEY is provided in headers."""
    def has_permission(self, request, view):
        key = request.headers.get('X-Gateway-Auth')
        return key == settings.GATEWAY_API_KEY
