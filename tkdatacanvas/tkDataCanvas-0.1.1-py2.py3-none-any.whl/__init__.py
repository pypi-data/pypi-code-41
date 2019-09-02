"""A tabular data display widget for Tkinter.

tkDataCanvas is a tabular data display widget for Python + Tkinter.
It is intended as a more efficient replacement for tkMagicGrid and
tkScrolledFrame for displaying large amounts of static data.

tkDataCanvas is designed to be simple above all else. It has no
dependencies outside the Python standard library. Its API is designed
to let you accomplish tasks with as few method calls as possible.
"""

from .widget import DataCanvas

# The only thing we need to publicly export is the widget
__all__ = ["DataCanvas"]
