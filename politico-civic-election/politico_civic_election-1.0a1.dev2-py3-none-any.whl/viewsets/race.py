# Imports from election.
from election.models import Race
from election.serializers import RaceSerializer
from election.viewsets.base import BaseViewSet


class RaceViewSet(BaseViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
