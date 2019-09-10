from ipywidgets import Box, register, Widget
from traitlets import Dict, Tuple, Unicode
from .sidecore import SidePanelCore


def _set(tuple, index, item):
    l = list(tuple)
    l[index] = item
    return l


def _insert(tuple, index, item):
    l = list(tuple)
    l.insert(index, item)
    return l


def _remove(tuple, index):
    l = list(tuple)
    del l[index]
    return l


@register
class SidePanel(SidePanelCore, Box):
    _model_name = Unicode('SidePanelModel').tag(sync=True)
    _view_name = Unicode('SidePanel').tag(sync=True)

    title = Unicode('No title').tag(sync=True)
    side = Unicode('split-right').tag(sync=True)
    ref = Unicode(None, allow_none=True).tag(sync=True)

    _ctrls = Dict().tag(sync=True)

    def __init__(self, widgets=None, **kwargs):
        super().__init__(**kwargs)
        self._view_count = 0
        if widgets is not None:
            if isinstance(widgets, Widget) or isinstance(widgets, tuple):
                widgets = [widgets]
            for w in widgets:
                if isinstance(w, Widget):
                    w, args = w, []
                elif isinstance(w, tuple):
                    w, *args = w
                else:
                    raise ValueError('Each child must be a Widget or a tuple (Widget, *header, *show, *expand) '
                                     'where the last three are optional')
                self.add(w, *args)

    def add(self, widget, header='', show=True, expand=True):
        self.insert(len(self.children), widget, header, show, expand)

    def insert(self, index, widget, header='', show=True, expand=True):
        self.children = _insert(self.children, index, widget)
        self._ctrls[widget.model_id] = (header, show, expand)
        self.send_state('_ctrls')

    def remove(self, item):
        if isinstance(item, Widget):
            idx = self.children.index(item)
        else:
            idx = int(item)
        self.children = _remove(self.children, idx)
        del self._ctrls[item.model_id]
        self.send_state('_ctrls')

    def _model_id(self, item):
        if not isinstance(item, Widget):
            item = self.children[int(item)]
        return item.model_id

    def set_header(self, item, header):
        model_id = self._model_id(item)
        h, s, e = self._ctrls[model_id]
        self._ctrls[model_id] = header, s, e
        self.send_state('_ctrls')

    def get_header(self, item):
        model_id = self._model_id(item)
        return self._ctrls[model_id][0]

    def expand(self, item, value):
        model_id = self._model_id(item)
        h, s, e = self._ctrls[model_id]
        self._ctrls[model_id] = h, s, value
        self.send_state('_ctrls')

    def is_expand(self, item):
        model_id = self._model_id(item)
        return self._ctrls[model_id][2]

    def show(self, item, value=True):
        model_id = self._model_id(item)
        h, s, e = self._ctrls[model_id]
        self._ctrls[model_id] = h, value, e
        self.send_state('_ctrls')

    def hide(self, item):
        self.show(item, False)

    def is_shown(self, item):
        model_id = self._model_id(item)
        return self._ctrls[model_id][1]
