


from .HAbstractElement import HAbstractElement



class HText(HAbstractElement):

	def __init__(self, text:str):
		self.text = text
		self.tag = None
	#

	def isDeepEqualTo(self, obj) -> bool:
		if isinstance(obj, HText):
			return obj.text == self.text
		else:
			return False
	#

	def isShallowEqualTo(self, obj) -> bool:
		if isinstance(obj, HText):
			return obj.text == self.text
		else:
			return False
	#

	def deepClone(self):
		return HText(self.text)
	#

	def toPlainText(self, HWriter) -> str:
		raise NotImplementedError()
	#

#




















