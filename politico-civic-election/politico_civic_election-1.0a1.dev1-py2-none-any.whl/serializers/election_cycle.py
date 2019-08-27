# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import ElectionCycle


class ElectionCycleSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = ElectionCycle
        fields = "__all__"
