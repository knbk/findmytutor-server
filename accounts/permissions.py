from rest_framework import permissions

from accounts.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsParentOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        parent = view.get_parent_object()
        return parent.user == request.user


class IsStudent(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.type == User.STUDENT
