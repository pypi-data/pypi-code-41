# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import Race


class RaceSerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = Race
        fields = "__all__"
