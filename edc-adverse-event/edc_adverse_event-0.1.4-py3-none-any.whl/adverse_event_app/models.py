from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_adverse_event.model_mixins import (
    AeModelMixin, SaeModelMixin, SUSARModelMixin, AeFollowupModelMixin)


class AeInitial(
    AeModelMixin, SaeModelMixin, SUSARModelMixin, ActionModelMixin,
    TrackingModelMixin, SiteModelMixin, BaseUuidModel
):

    pass


class AeFollowup(AeFollowupModelMixin, BaseUuidModel):

    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeFollowupModelMixin.Meta):
        pass


class AeSusar(AeFollowupModelMixin, BaseUuidModel):

    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    class Meta(AeFollowupModelMixin.Meta):
        pass
