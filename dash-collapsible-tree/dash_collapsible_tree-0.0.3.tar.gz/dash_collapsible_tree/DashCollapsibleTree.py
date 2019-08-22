# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashCollapsibleTree(Component):
    """A DashCollapsibleTree component.


Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks
- data (dict; optional)"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.UNDEFINED, onChange=Component.UNDEFINED, onAction=Component.UNDEFINED, onNodeToggle=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'data']
        self._type = 'DashCollapsibleTree'
        self._namespace = 'dash_collapsible_tree'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashCollapsibleTree, self).__init__(**args)
