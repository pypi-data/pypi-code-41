# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from election.
from election.models import Candidate


class CandidateSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = Candidate
        fields = "__all__"
