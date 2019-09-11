


class HAbstractElement(object):

	def isDeepEqualTo(self, obj) -> bool:
		raise NotImplementedError()
	#

	def isShallowEqualTo(self, obj) -> bool:
		raise NotImplementedError()
	#

	def deepClone(self):
		raise NotImplementedError()
	#

#




















