# Imports from election.
from election.models import ElectionCycle
from election.serializers import ElectionCycleSerializer
from election.viewsets.base import BaseViewSet


class ElectionCycleViewSet(BaseViewSet):
    queryset = ElectionCycle.objects.all()
    serializer_class = ElectionCycleSerializer
