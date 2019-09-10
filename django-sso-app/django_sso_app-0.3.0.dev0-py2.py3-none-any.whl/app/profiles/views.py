import logging

from rest_framework import permissions
from rest_framework import viewsets

from django_sso_app.core.permissions import is_staff
from .models import Profile
from .serializers import ProfileSerializer, ProfilePublicSerializer

logger = logging.getLogger('profiles')


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'sso_id'

    def get_queryset(self):
        user = self.request.user
        if is_staff(user):
            return Profile.objects.all()
        else:
            return Profile.objects.filter(user=user)

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ProfileSerializer
        else:
            return ProfilePublicSerializer

    def list(self, request, *args, **kwargs):
        """
        List profiles
        """
        return super(ProfileViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Profile detail
        """
        return super(ProfileViewSet, self).retrieve(request, *args, **kwargs)
