

from .HAbstractElement import HAbstractElement
from .HText import HText
from .HAttribute import HAttribute
from .HAttributeList import HAttributeList
from .HElement_HAbstractElementList import HAbstractElementList, HElement

from .EnumTextTrimMode import EnumTextTrimMode
from .EnumWhiteSpaceProcessing import EnumWhiteSpaceProcessing
from .EnumXMLPrintStyle import EnumXMLPrintStyle
from .EnumXMLTextOutputEncoding import EnumXMLTextOutputEncoding
from .XMLWriteSettings import XMLWriteSettings

from .HToolkit_Write_PlainText import HToolkit_Write_PlainText
from .HToolkit_Write_XML import HToolkit_Write_XML
from .HToolkit_Write_Dump import HToolkit_Write_Dump
from .HToolkit_Write_HTML import HToolkit_Write_HTML

from jk_hwriter import HWriter as _HWriter



class HSerializer(object):

	writeXML = HToolkit_Write_XML.writeXML

	@staticmethod
	def toXMLStr(root:HElement, xmlWriteSettings:XMLWriteSettings) -> str:
		w = _HWriter()
		HToolkit_Write_XML.writeXML(root, w, xmlWriteSettings)
		return str(w)
	#

	@staticmethod
	def printXML(root:HElement, xmlWriteSettings:XMLWriteSettings):
		w = _HWriter()
		HToolkit_Write_XML.writeXML(root, w, xmlWriteSettings)
		print(w)
	#

	writeDump = HToolkit_Write_Dump.writeDump

	@staticmethod
	def toDumpStr(root:HElement, _ = None) -> str:
		w = _HWriter()
		HToolkit_Write_Dump.writeDump(root, w)
		return str(w)
	#

	@staticmethod
	def printDump(root:HElement, _ = None):
		w = _HWriter()
		HToolkit_Write_Dump.writeDump(root, w)
		print(w)
	#

	"""
	writePlainText = HToolkit_Write_PlainText.writePlainText

	@staticmethod
	def toPlainText(root:HElement, _ = None) -> str:
		w = _HWriter()
		HToolkit_Write_PlainText.writePlainText(root, w)
		return str(w)
	#

	@staticmethod
	def printPlainText(root:HElement, _ = None):
		w = _HWriter()
		HToolkit_Write_PlainText.writePlainText(root, w)
		print(w)
	#
	"""

	writeHTMLDoc = HToolkit_Write_HTML.writeHTMLDoc
	writeHTML = HToolkit_Write_HTML.writeHTML

	@staticmethod
	def toHTMLStr(root:HElement, _ = None) -> str:
		w = _HWriter()
		HToolkit_Write_HTML.writeHTML(root, w)
		return str(w)
	#

	@staticmethod
	def toHTMLDocStr(root:HElement, _ = None) -> str:
		w = _HWriter()
		HToolkit_Write_HTML.writeHTMLDoc(root, w)
		return str(w)
	#

	@staticmethod
	def printHTML(root:HElement, _ = None):
		w = _HWriter()
		HToolkit_Write_HTML.writeHTML(root, w)
		print(w)
	#

	@staticmethod
	def printHTMLDoc(root:HElement, _ = None):
		w = _HWriter()
		HToolkit_Write_HTML.writeHTMLDoc(root, w)
		print(w)
	#

#




__version__ = "0.2019.9.11"



