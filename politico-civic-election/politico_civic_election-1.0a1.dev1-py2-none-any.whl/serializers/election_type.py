# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import ElectionType


class ElectionTypeSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = ElectionType
        fields = "__all__"
