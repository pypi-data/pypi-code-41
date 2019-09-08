# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import Election


class ElectionSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = Election
        fields = "__all__"
