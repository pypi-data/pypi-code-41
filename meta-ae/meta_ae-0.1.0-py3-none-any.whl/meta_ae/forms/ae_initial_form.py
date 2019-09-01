from edc_adverse_event.forms import AeInitialForm as BaseAeInitialForm

from ..models import AeInitial, AeFollowup


class AeInitialForm(BaseAeInitialForm):

    ae_followup_model_cls = AeFollowup

    class Meta:
        model = AeInitial
        fields = "__all__"
