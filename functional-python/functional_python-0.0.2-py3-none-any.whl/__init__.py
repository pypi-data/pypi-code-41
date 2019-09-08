from collections import namedtuple

__pdoc__ = { }
__title__ = 'functional-python'
__author__ = 'Peter Zaitcev / USSX Hares'
__license__ = 'BSD 2-clause'
__copyright__ = 'Copyright 2019 Peter Zaitcev'
__version__ = '0.0.2'

_VersionInfo = namedtuple('_VersionInfo', 'major minor micro releaselevel serial')
__pdoc__['_VersionInfo.major'] = 'Library major release. Backwards-compatibility is not guaranteed across different major releases.'
__pdoc__['_VersionInfo.minor'] = 'Library minor release. Minor releases are backwards-compatible patches distributing some new functionality.'
__pdoc__['_VersionInfo.micro'] = 'Library micro release. Micro releases contain only fixes/patches and do no distribute any new functionality.'
__pdoc__['_VersionInfo.releaselevel'] = 'Library release level. Defines the production cycle state of the library.'
version_info = _VersionInfo(major=0, minor=0, micro=1, releaselevel='alpha', serial=0)

from .predef import *
from .containers import *
from .monads import *

from .option import *
