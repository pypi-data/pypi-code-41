from ipywidgets import Widget
from traitlets import Unicode

from ._version import EXTENSION_SPEC_VERSION

MODULE_NAME = "sidepanel"


class SidePanelCore(Widget):
    _model_module = Unicode(MODULE_NAME).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
    _view_module = Unicode(MODULE_NAME).tag(sync=True)
    _view_module_version = Unicode(EXTENSION_SPEC_VERSION).tag(sync=True)
