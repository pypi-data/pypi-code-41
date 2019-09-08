import sys
from robot.api.deco import keyword

class Keywords(object):
    '''
    top level keyword definition
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self._tst = None

    ###########################################################################
    @keyword(name="get_python_version")
    ###########################################################################
    def get_python_version(self):
        return sys.version