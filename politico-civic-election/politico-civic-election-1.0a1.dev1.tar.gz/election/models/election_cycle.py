# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from uuslug import slugify


class ElectionCycle(CommonIdentifiersMixin, CivicBaseModel):

    natural_key_fields = ["slug"]
    uid_prefix = "cycle"
    uid_base_field = "name"
    default_serializer = "election.serializers.ElectionCycleSerializer"

    name = models.CharField(max_length=4)

    def __str__(self):
        return self.uid

    def save(self, *args, **kwargs):
        """
        **uid field/identifier**: :code:`cycle:{year}`
        """
        self.generate_common_identifiers(
            always_overwrite_slug=True, always_overwrite_uid=True
        )

        super(ElectionCycle, self).save(*args, **kwargs)

    def get_uid_suffix(self):
        return self.slug
