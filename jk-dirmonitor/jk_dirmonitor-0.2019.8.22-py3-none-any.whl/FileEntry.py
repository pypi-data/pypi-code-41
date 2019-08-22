


import os




class FileEntry(object):

	def __init__(self, name:str, path:str, timeStamp:int, size:int):
		self._name = name
		self._timeStamp = timeStamp
		self._size = size
		self._path = path
	#

	@property
	def path(self) -> str:
		return self._path
	#

	@property
	def name(self) -> str:
		return self._name
	#

	@property
	def timeStamp(self) -> int:
		return self._timeStamp
	#

	@property
	def size(self) -> int:
		return self._size
	#

	#def stat(self) -> os.stat_result:
	#	return os.stat(self._path)
	##

	def __str__(self):
		return self._name
	#

	def __repr__(self):
		return self._name
	#

#





