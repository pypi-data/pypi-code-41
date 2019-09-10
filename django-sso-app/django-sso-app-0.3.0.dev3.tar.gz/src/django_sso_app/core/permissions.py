import logging

from rest_framework import permissions


def is_staff(user):
    return user and (user.is_staff or user.groups.filter(name='staff').count() > 0)


class OwnerPermission(permissions.IsAuthenticated):

    message = 'You must be the owner.'

    def has_object_permission(self, request, view, obj):
        if (getattr(request, 'user', None) is not None and request.user == obj):
            return True
        return False


class StaffPermission(permissions.IsAuthenticated):
    message = 'You must be a staff member.'

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return False


class OwnerOrStaffPermission(permissions.IsAuthenticated):

    message = 'You must be the owner or a staff member.'

    def has_object_permission(self, request, view, obj):
        if (request.user == obj) or request.user.is_staff:
            return True
        return False


class PublicObjectOrOwnerOrStaffPermission(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        user = request.user
        user_is_staff = is_staff(user)

        if user_is_staff:
            return True

        is_public = getattr(obj, 'is_public', False)
        has_owner = getattr(obj, 'user', False)

        if (is_public and not has_owner) and not user_is_staff:
            return False

        if is_public:
            return True

        obj_user = getattr(obj, 'user', None)

        return obj_user == user
