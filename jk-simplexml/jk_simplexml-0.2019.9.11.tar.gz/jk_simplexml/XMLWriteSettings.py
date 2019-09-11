

import jk_console

from .EnumXMLPrintStyle import EnumXMLPrintStyle
from .EnumXMLTextOutputEncoding import EnumXMLTextOutputEncoding
from .HElement_HAbstractElementList import HElement







class _MyStrategy(object):

	def __init__(self, names:list):
		self.__names = set()
		self.__names.extend(names)
	#

	def checkOutputTextAsInlineCallback(parentElement:HElement, currentElement:HElement) -> bool:
		return currentElement.name in self.__name
	#

#



class XMLWriteSettings(object):

	def __init__(self):
		self.writeXmlHeader = True
		self.printStyle = EnumXMLPrintStyle.Pretty
		self.textEncoding = EnumXMLTextOutputEncoding.EncodeReservedCharsAsEntities
		self.attributeEncoding = EnumXMLTextOutputEncoding.EncodeReservedCharsAsEntities
		self.checkInlineOverride = None
		self.colorSchema = None
	#

	def setCheckInlineOverrideByElementNames(self, names):
		s = _MyStrategy(names)
		self.checkInlineOverride = s.checkOutputTextAsInlineCallback
	#

	def setXMLColorSchema(self, metaColor:str, tagDelimiterColor:str, tagNameColor:str, attributeNameColor:str, attributeValueColor:str, textColor:str, specialColor:str):
		self.colorSchema = {
			"d": tagDelimiterColor,
			"tn": tagNameColor,
			"an": attributeNameColor,
			"av": attributeValueColor,
			"t": textColor,
			"m": metaColor,
			"s": specialColor,
			"r": jk_console.Console.RESET,
		}
	#

	def setDefaultXMLColorSchema(self):
		self.setXMLColorSchema(
			metaColor = jk_console.Console.ForeGround.STD_LIGHTRED,
			tagDelimiterColor = jk_console.Console.ForeGround.STD_LIGHTGRAY,
			tagNameColor = jk_console.Console.ForeGround.STD_YELLOW,
			attributeNameColor = jk_console.Console.ForeGround.STD_LIGHTCYAN,
			attributeValueColor = jk_console.Console.ForeGround.STD_CYAN,
			textColor = jk_console.Console.ForeGround.STD_LIGHTBLUE,
			specialColor = jk_console.Console.ForeGround.STD_LIGHTGREEN
			)
	#

#












