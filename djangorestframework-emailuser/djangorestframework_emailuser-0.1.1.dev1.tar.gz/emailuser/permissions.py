from rest_framework import permissions

class IsSelfOrReadOnly(permissions.BasePermission):
    """Allow access if readonly or if the user object is the user."""
    message = 'Only the logged in owner can modify a user.'
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj