##############################################
##### Utilities for mcautograder library #####
##############################################

import pickle

def repeat(x, n):
	"""
	Returns a list of a given value repeated a given number of times

	Args:

	* `x` (any): The value to repeat
	* `n` (`int`): The number of repetitions

	Returns:

	* `list`. List of repeated values `x`
	"""
	return [x for _ in range(n)]

def serialize(obj, file):
	"""
	Serializes an object and writes its bytes to a file

	Args:
	
	* `obj` (any): Object to be serialized
	* `file` (file object): File to write bytes into
	"""
	pickle.dump(obj, file, protocol=pickle.HIGHEST_PROTOCOL)