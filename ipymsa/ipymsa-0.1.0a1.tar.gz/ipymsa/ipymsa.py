import ipywidgets as widgets
from traitlets import Unicode


@widgets.register
class IpyMsa(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('MsaView').tag(sync=True)
    _model_name = Unicode('MsaModel').tag(sync=True)
    _view_module = Unicode('ipymsa').tag(sync=True)
    _model_module = Unicode('ipymsa').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode(">seq1\nACT-\n>seq2\nACGG\n").tag(sync=True)
