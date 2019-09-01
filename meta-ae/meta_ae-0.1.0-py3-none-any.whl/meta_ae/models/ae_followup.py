from django.db import models
from django.db.models.deletion import PROTECT
from edc_adverse_event.model_mixins import AeFollowupModelMixin
from edc_model.models.base_uuid_model import BaseUuidModel


class AeFollowup(AeFollowupModelMixin, BaseUuidModel):

    ae_initial = models.ForeignKey("meta_ae.aeinitial", on_delete=PROTECT)

    class Meta(AeFollowupModelMixin.Meta):
        pass
