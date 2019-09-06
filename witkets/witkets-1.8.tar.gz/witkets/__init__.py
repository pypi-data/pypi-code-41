__version__ = '1.8'

# =============================================================================
# Subpackages
# =============================================================================

from . import core
from . import plot
from . import scripts

# =============================================================================
# Basic Widgets
# =============================================================================

from .accellabel import AccelLabel
from .cardlayout import CardLayout
from .colorbutton import ColorButton
from .consoleview import ConsoleView
from .coordsys import CoordSys2D, CoordConverter
from .expander import Expander
from .filechooserentry import FileChooserEntry, FileChooserAction
from .gauge import Gauge
from .imagebutton import ImageButton
from .imagemap import ImageMap
from .ipytext import IPyText
from .led import Shapes, LED
from .ledbar import LEDBar
from .linkbutton import LinkButton
from .logicswitch import LogicSwitch
from .numericlabel import NumericLabel
from .pytext import PyText
from .pyscrolledtext import PyScrolledText
from .ribbon import Ribbon
from .spin import Spin
from .spinner import Spinner
from .tank import Tank
from .themedlabelframe import ThemedLabelFrame
from .thermometer import Thermometer
from .timeentry import TimeEntry
from .togglebutton import ToggleButton
from .toolbar import Toolbar

# =============================================================================
# Dynamic Building and Styling
# =============================================================================

from .style import Style
from .tkbuilder import TkBuilder
