# Imports from election.
from election.models import ElectionType
from election.serializers import ElectionTypeSerializer
from election.viewsets.base import BaseViewSet


class ElectionTypeViewSet(BaseViewSet):
    queryset = ElectionType.objects.all()
    serializer_class = ElectionTypeSerializer
