
from blinker import signal

from .libraries import gather_libraries, gather_python
from .version import __version__

liveliness_probe = signal('oarepo.probe.liveliness')
readiness_probe = signal('oarepo.probe.readiness')
environ_probe = signal('oarepo.probe.environ')

environ_probe.connect(gather_libraries)
environ_probe.connect(gather_python)

__all__ = ('__version__', 'liveliness_probe', 'readiness_probe', 'environ_probe')
