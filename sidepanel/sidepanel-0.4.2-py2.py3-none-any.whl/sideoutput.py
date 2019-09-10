from ipywidgets import Output, register
from traitlets import Unicode

from .sidecore import SidePanelCore

MODULE_NAME = "sidepanel"


@register
class SideOutput(Output, SidePanelCore):
    _model_name = Unicode('SideOutputModel').tag(sync=True)
    _view_name = Unicode('Side').tag(sync=True)

    title = Unicode('SideOutput').tag(sync=True)
    side = Unicode('split-right').tag(sync=True)
    ref = Unicode(None, allow_none=True).tag(sync=True)

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        self._view_count = 0
