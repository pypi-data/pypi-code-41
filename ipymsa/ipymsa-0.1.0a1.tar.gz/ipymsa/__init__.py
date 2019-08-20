from ._version import version_info, __version__

from .ipymsa import *


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'ipymsa',
        'require': 'ipymsa/extension'
    }]
