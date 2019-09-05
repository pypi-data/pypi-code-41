# License MIT
#
# Authors: Vladimir Udartsev <v.udartsev@gmail.com>
#
# """Creating simple print of objects for better code debugging"""

from pprint import pprint
from inspect import getmembers

def var_dump(object):
	"""Print var data recursevly to console"""
	data = getmembers(object)
	results = pprint(data)

	return results

