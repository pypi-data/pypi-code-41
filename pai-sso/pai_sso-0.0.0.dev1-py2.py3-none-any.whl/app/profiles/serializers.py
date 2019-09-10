import logging

from rest_framework.reverse import reverse

from .models import Profile
from pai_sso.core.serializers import AbsoluteUrlSerializer

logger = logging.getLogger('serializers')


class ProfileSerializer(AbsoluteUrlSerializer):

    class Meta:
        model = Profile
        read_only_fields = (
            'url',
            'created_at', 'sso_id', 'sso_rev', 'username', 'email',
            'first_name', 'last_name', 'description', 'birthdate', 'picture',
            'latitude', 'longitude', 'country', 'address')
        fields = read_only_fields

    def get_absolute_url(self, obj):
        if getattr(obj, 'id', None) is not None:
            request = self.context['request']
            reverse_url = reverse('profile:detail', args=[obj.sso_id])
            return request.build_absolute_uri(reverse_url)


class ProfilePublicSerializer(ProfileSerializer):

    class Meta:
        model = Profile
        read_only_fields = (
            'url',
            'sso_id',
            'created_at', 'username', 'picture',
            'latitude', 'longitude', 'country')
        fields = read_only_fields
