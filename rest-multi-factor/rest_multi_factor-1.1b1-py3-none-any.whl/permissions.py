"""Permission classes for multi factor requiring REST APIs."""

__all__ = (
    "IsVerified",
    "IsTokenAuthenticated",
    "IsVerifiedOrNoDevice"
)

from django import VERSION
from django.db.models.query import Q


from rest_framework.permissions import BasePermission


from rest_multi_factor.utils import unify_queryset
from rest_multi_factor.models import Device
from rest_multi_factor.settings import multi_factor_settings


class IsTokenAuthenticated(BasePermission):
    """
    Permission that requires token authentication.

    This permission requires that every request is made
    with a API token, instead of for example basic auth.
    """

    def has_permission(self, request, view):
        """
        Tell whether or not the user has a API token.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view that is being accessed
        :type view: rest_framework.views.APIView

        :return: Whether permission is granted or not
        :rtype: bool
        """
        return bool(
            request.user and request.user.is_authenticated
            and request.auth is not None
        )


class IsVerified(IsTokenAuthenticated):
    """
    Permission that requires multi factor.

    This permission requires that the token is completely verified.
    """

    backend_class = multi_factor_settings.DEFAULT_BACKEND_CLASS

    def has_permission(self, request, view):
        """
        Tell whether or not the user has a verified API token.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view that is being accessed
        :type view: rest_framework.views.APIView

        :return: Whether permission is granted or not
        :rtype: bool
        """
        backend = self.get_backend()
        counted = backend.verify(request.auth, view)

        return (
            IsTokenAuthenticated.has_permission(self, request, view)
            and counted == 0
        )

    def get_backend(self):
        """
        Instantiate the backend class and returns it.

        :return: The backend class to use
        :rtype: rest_multi_factor.backends.AbstractVerificationBackend
        """
        assert self.backend_class is not None, (
            "'{0}' should either include a `backend_class` attribute, "
            "or override the `get_backend()` method."
            .format(self.__class__.__name__)
        )

        return self.backend_class()


class IsVerifiedOrNoDevice(IsVerified):
    """
    Permission that requires multi factor if available.

    This permission allows access if completely verified
    or if no device is registered. This can be useful for
    first time requirement of multi factor.
    """

    def has_permission(self, request, view):
        """
        Tell whether or not the user has permission.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view that is being accessed
        :type view: rest_framework.views.APIView

        :return: Whether permission is granted or not
        :rtype: bool
        """
        return (
                IsVerified.has_permission(self, request, view)
                or not self.has_devices(request.user)
        )

    def has_devices(self, user):
        """
        Check if the user has any devices registered.

        :param user: The current user
        :type user: django.contrib.auth.model.AbstractBaseUser

        :return: Whether the current user has devices or not
        :rtype: bool
        """
        queryset = unify_queryset(Device, ("id",), Q(user=user))

        # ticket: https://code.djangoproject.com/ticket/28399
        if VERSION < (1, 11, 4):
            return bool(len(queryset))  # pragma: no cover

        return bool(queryset.count())   # pragma: no cover
