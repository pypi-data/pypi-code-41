# Imports from election.
from election.models import Election
from election.serializers import ElectionSerializer
from election.viewsets.base import BaseViewSet


class ElectionViewSet(BaseViewSet):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
