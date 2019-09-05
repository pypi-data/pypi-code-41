# License MIT
#
# Authors: Vladimir Udartsev <v.udartsev@gmail.com>

from pprint import pprint
from inspect import getmembers

__version__ = '0.0.1'

class var_dump():
    """Creating simple print of objects for better code debugging"""
    @staticmethod
    def var_dump(object, printIt=True):
        """Print var data recursevly to console"""

        data = getmembers(object)
        results = pprint(data)

        # if printIt is True:
        #    print(results)

        return results

