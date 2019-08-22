from __future__ import unicode_literals

import ipywidgets as widgets
from traitlets import Int, Unicode

MODULE_NAME = 'mlviswidget'
VERSION = '0.0.1'

class Widget(widgets.DOMWidget):
    _model_module = Unicode(MODULE_NAME).tag(sync=True)
    _model_name = Unicode('WidgetModel').tag(sync=True)
    _model_module_version = Unicode(VERSION).tag(sync=True)
    _view_module = Unicode(MODULE_NAME).tag(sync=True)
    _view_name = Unicode('WidgetView').tag(sync=True)
    _view_module_version = Unicode(VERSION).tag(sync=True)

    props = Unicode('{}').tag(sync=True)
    component_name = Unicode('').tag(sync=True)
    widget_id = Unicode('', help="Parent message id of messages to capture").tag(sync=True)
