from rest_framework.reverse import reverse

from ...serializers import AbsoluteUrlSerializer
from .models import Group


class GroupSerializer(AbsoluteUrlSerializer):
    class Meta:
        model = Group
        read_only_fields = ('url', 'id', 'name')
        fields = read_only_fields
