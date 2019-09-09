import sys
from robot.api.deco import keyword

class Party(object):
    """A library for *documentation format* demonstration purposes.

    __ http://docutils.sourceforge.net
    """

    ROBOT_LIBRARY_DOC_FORMAT = 'reST'
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._tst = None

    ###########################################################################
    @keyword(name="get_python_version")
    ###########################################################################
    def get_python_version(self):
        return sys.version
