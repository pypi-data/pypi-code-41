# Dynamically build component wrappers utilizing the ipywidget
import sys, json
from .widget import Widget
from traitlets import Unicode

current_module = sys.modules[__name__]


def init(self, props={}):
    Widget.__init__(self)
    self.props = json.dumps(props)


components = [
    'AreaChart',
    'StackedCalendar',
    'GraphBuilder',
    'FeatureListView',
    'MultiWayPlot',
    'Manifold'
]


# Dynamically create module classes
for component in components:
    setattr(current_module,
            component,
            type(component,
                (Widget, ),
                {
                    '__init__': init,
                    'component_name': Unicode(component).tag(sync=True)
                }))
