from rest_framework import permissions


# Permissions mixins

class OwnerPermission(permissions.BasePermission):

    message = 'You must be the owner.'

    def has_object_permission(self, request, view, obj):
        if (request.user == obj):
            return True
        return False

class StaffPermission(permissions.BasePermission):
    message = 'You must be a staff member.'

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return False

class OwnerOrStaffPermission(permissions.BasePermission):

    message = 'You must be the owner or a staff member.'

    def has_object_permission(self, request, view, obj):
        if (request.user == obj) or request.user.is_staff:
            return True
        return False
