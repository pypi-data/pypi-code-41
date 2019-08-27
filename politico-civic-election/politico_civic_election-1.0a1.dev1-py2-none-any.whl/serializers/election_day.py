# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import ElectionDay


class ElectionDaySerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = ElectionDay
        fields = "__all__"
