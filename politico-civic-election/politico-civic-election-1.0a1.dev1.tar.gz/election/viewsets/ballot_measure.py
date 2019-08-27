# Imports from election.
from election.models import BallotMeasure
from election.serializers import BallotMeasureSerializer
from election.viewsets.base import BaseViewSet


class BallotMeasureViewSet(BaseViewSet):
    queryset = BallotMeasure.objects.all()
    serializer_class = BallotMeasureSerializer
