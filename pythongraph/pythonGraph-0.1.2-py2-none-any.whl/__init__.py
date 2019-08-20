from pbr import version

from .pythonGraph import *  # noqa: F401, F403


__version__ = version.VersionInfo('pythonGraph').release_string()
print('{} {}'.format(__name__, __version__))
