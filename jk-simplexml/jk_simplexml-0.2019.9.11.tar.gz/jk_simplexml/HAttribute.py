


from .HAbstractElement import HAbstractElement



class HAttribute(HAbstractElement):

	def __init__(self, name:str, value:str):
		self.name = name
		self.value = value
		self.tag = None
	#

	def isDeepEqualTo(self, obj) -> bool:
		if isinstance(obj, HAttribute):
			return (obj.name == self.name) and (obj.value == self.value)
		else:
			return False
	#

	def isShallowEqualTo(self, obj) -> bool:
		if isinstance(obj, HAttribute):
			return (obj.name == self.name) and (obj.value == self.value)
		else:
			return False
	#

	def deepClone(self):
		return HAttribute(self.name, self.value)
	#

	def __str__(self):
		if self.value is None:
			return self.name
		else:
			return self.name + "=\"" + self.value + "\""
	#

	def __repr__(self):
		if self.value is None:
			return self.name
		else:
			return self.name + "=\"" + self.value + "\""
	#

	def toPlainText(self, HWriter) -> str:
		raise NotImplementedError()
	#

#




















