



from jk_hwriter import HWriter
from jk_console import Console

from .HElement_HAbstractElementList import *
from .XMLWriteSettings import *
from .ImplementationErrorException import ImplementationErrorException




class HToolkit_Write_XML(object):

	@staticmethod
	def writeXML(root:HElement, w:HWriter, xmlWriteSettings:XMLWriteSettings):
		assert isinstance(root, HElement)
		assert isinstance(xmlWriteSettings, XMLWriteSettings)
		assert isinstance(w, HWriter)

		HToolkit_Write_XML._writeAsXML(root, xmlWriteSettings, None, None, w)
	#

	@staticmethod
	def _writeAsXML(root:HElement, xmlWriteSettings:XMLWriteSettings, specialElements2:list, specialElements:list, w:HWriter):
		if xmlWriteSettings.writeXmlHeader:
			w.write(xmlWriteSettings.colorSchema["m"] if xmlWriteSettings.colorSchema else "", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>", Console.RESET)
			if xmlWriteSettings.printStyle != EnumXMLPrintStyle.SingleLine:
				w.writeLn()
		if specialElements2 is not None:
			for specialElement in specialElements2:
				w.write(xmlWriteSettings.colorSchema["s"] if xmlWriteSettings.colorSchema else "", specialElement, Console.RESET)
				if xmlWriteSettings.printStyle != EnumXMLPrintStyle.SingleLine:
					w.writeLn()
		if specialElements is not None:
			for specialElement in specialElements:
				HToolkit_Write_XML.__writeXmlSpecialTag(specialElement, w)
				if xmlWriteSettings.printStyle != EnumXMLPrintStyle.SingleLine:
					w.writeLn()

		if xmlWriteSettings.printStyle == EnumXMLPrintStyle.Pretty:
			if xmlWriteSettings.checkInlineOverride is not None:
				if xmlWriteSettings.checkInlineOverride(None, root):
					HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, root, True, w)
				else:
					HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, root, False, w)
			else:
				HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, root, False, w)
		elif xmlWriteSettings.printStyle == EnumXMLPrintStyle.Simple:
			HToolkit_Write_XML.__addXmlSimple(xmlWriteSettings, root, False, w)
		elif xmlWriteSettings.printStyle == EnumXMLPrintStyle.SingleLine:
			HToolkit_Write_XML.__addXmlSingleLine(xmlWriteSettings, root, w)
			w.writeLn()
		else:
			raise ImplementationErrorException("(None)" if xmlWriteSettings is None else str(xmlWriteSettings.printStyle))
	#

	@staticmethod
	def __addXmlPretty(xmlWriteSettings:XMLWriteSettings, e:HElement, bForceInline:bool, w:HWriter):
		if bForceInline:
			HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
			for eChild in e.children:
				if isinstance(eChild, HElement):
					HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, "", eChild, True, w)
				else:
					if isinstance(eChild, HText):
						HToolkit_Write_XML.__addXmlText(xmlWriteSettings, eChild, w)
					else:
						raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
			HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
			return

		if len(e.children) == 0:
			HToolkit_Write_XML.__writeXmlOpeningClosingTag(xmlWriteSettings, e, w)
			w.writeLn()
		else:
			if e.hasOnlyTexts:
				HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
				for eChild in e.children:
					if isinstance(eChild, HText):
						HToolkit_Write_XML.__addXmlText(xmlWriteSettings, eChild, w)
					else:
						raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
				HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
				w.writeLn()
			else:
				HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
				w.writeLn()
				w.incrementIndent()
				for eChild in e.children:
					if isinstance(eChild, HElement):
						if bForceInline:
							HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, eChild, True, w)
						else:
							bForceInlineNew = False if xmlWriteSettings.checkInlineOverride is None else xmlWriteSettings.checkInlineOverride(e, eChild)
							if bForceInlineNew:
								HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, eChild, bForceInlineNew, w)
								w.writeLn()
							else:
								HToolkit_Write_XML.__addXmlPretty(xmlWriteSettings, eChild, False, w)
					else:
						if isinstance(eChild, HText):
							HToolkit_Write_XML.__addXmlText(xmlWriteSettings, eChild, w)
							w.writeLn()
						else:
							raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
				w.decrementIndent()
				HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
				w.writeLn()
	#

	@staticmethod
	def __writeXmlOpeningTag(xmlWriteSettings:XMLWriteSettings, e:HElement, w:HWriter):
		c_d = xmlWriteSettings.colorSchema["d"] if xmlWriteSettings.colorSchema else ""
		c_tn = xmlWriteSettings.colorSchema["tn"] if xmlWriteSettings.colorSchema else ""
		c_an = xmlWriteSettings.colorSchema["an"] if xmlWriteSettings.colorSchema else ""
		c_av = xmlWriteSettings.colorSchema["av"] if xmlWriteSettings.colorSchema else ""
		c_r = xmlWriteSettings.colorSchema["r"] if xmlWriteSettings.colorSchema else ""

		w.write(
			c_d,
			"<",
			c_tn,
			e.name,
			c_r,
			)
		if len(e.attributes) > 0:
			for a in e.attributes:
				w.write(
					" ",
					c_an,
					a.name,
					c_d,
					"=",
					"\"",
					c_r
					)
				if ((a.value is not None) and (len(a.value) > 0)):
					HToolkit_Write_XML.__addXmlAttributeValue(xmlWriteSettings, a.value, w)
				w.write(
					c_d,
					"\"",
					c_r
					)
		w.write(
			c_d,
			">",
			c_r
			)
	#

	@staticmethod
	def __writeXmlOpeningClosingTag(xmlWriteSettings:XMLWriteSettings, e:HElement, w:HWriter):
		c_d = xmlWriteSettings.colorSchema["d"] if xmlWriteSettings.colorSchema else ""
		c_tn = xmlWriteSettings.colorSchema["tn"] if xmlWriteSettings.colorSchema else ""
		c_an = xmlWriteSettings.colorSchema["an"] if xmlWriteSettings.colorSchema else ""
		c_av = xmlWriteSettings.colorSchema["av"] if xmlWriteSettings.colorSchema else ""
		c_r = xmlWriteSettings.colorSchema["r"] if xmlWriteSettings.colorSchema else ""

		w.write(
			c_d,
			"<",
			c_tn,
			e.name,
			c_r
			)
		if len(e.attributes) > 0:
			for a in e.attributes:
				w.write(
					" ",
					c_an,
					a.name,
					c_d,
					"=",
					"\"",
					c_r
					)
				if ((a.value is not None) and (len(a.value) > 0)):
					HToolkit_Write_XML.__addXmlAttributeValue(xmlWriteSettings, a.value, w)
				w.write(
					c_d,
					"\"",
					c_r
					)
		w.write(
			c_d,
			"/>",
			c_r
			)
	#

	@staticmethod
	def __writeXmlClosingTag(xmlWriteSettings:XMLWriteSettings, e:HElement, w:HWriter):
		c_d = xmlWriteSettings.colorSchema["d"] if xmlWriteSettings.colorSchema else ""
		c_tn = xmlWriteSettings.colorSchema["tn"] if xmlWriteSettings.colorSchema else ""
		c_an = xmlWriteSettings.colorSchema["an"] if xmlWriteSettings.colorSchema else ""
		c_av = xmlWriteSettings.colorSchema["av"] if xmlWriteSettings.colorSchema else ""
		c_r = xmlWriteSettings.colorSchema["r"] if xmlWriteSettings.colorSchema else ""

		w.write(
			c_d,
			"</",
			c_tn,
			e.name,
			c_d,
			">",
			c_r
			)
	#

	@staticmethod
	def __addXmlAttributeValue(xmlWriteSettings:XMLWriteSettings, text:str, w:HWriter):
		c_d = xmlWriteSettings.colorSchema["d"] if xmlWriteSettings.colorSchema else ""
		c_tn = xmlWriteSettings.colorSchema["tn"] if xmlWriteSettings.colorSchema else ""
		c_an = xmlWriteSettings.colorSchema["an"] if xmlWriteSettings.colorSchema else ""
		c_av = xmlWriteSettings.colorSchema["av"] if xmlWriteSettings.colorSchema else ""
		c_r = xmlWriteSettings.colorSchema["r"] if xmlWriteSettings.colorSchema else ""
		c_t = xmlWriteSettings.colorSchema["t"] if xmlWriteSettings.colorSchema else ""

		if not text:
			return

		if xmlWriteSettings.attributeEncoding == EnumXMLTextOutputEncoding.AlwaysAsIs:
			w.write(
				c_av,
				text,
				c_r,
				)
		elif xmlWriteSettings.attributeEncoding == EnumXMLTextOutputEncoding.EncodeReservedCharsAsEntities:
			sb = [ c_av ]
			for c in text:
				if c == "\"":
					sb.append("&quot")
				elif c == "&":
					sb.append("&amp")
				elif c == "<":
					sb.append("&lt")
				elif c == ">":
					sb.append("&gt")
				else:
					sb.append(c)
			sb.append(c_r)
			w.write(*sb)
		elif xmlWriteSettings.attributeEncoding == EnumXMLTextOutputEncoding.OnReservedCharsOutputTextAsCData:
			raise Exception("Attributes are not allowed to contain CData!")
		else:
			raise ImplementationErrorException("(None)" if xmlWriteSettings is None else str(xmlWriteSettings.attributeEncoding))
	#

	@staticmethod
	def __addXmlText(xmlWriteSettings:XMLWriteSettings, htext:HText, w:HWriter):
		c_d = xmlWriteSettings.colorSchema["d"] if xmlWriteSettings.colorSchema else ""
		c_tn = xmlWriteSettings.colorSchema["tn"] if xmlWriteSettings.colorSchema else ""
		c_an = xmlWriteSettings.colorSchema["an"] if xmlWriteSettings.colorSchema else ""
		c_av = xmlWriteSettings.colorSchema["av"] if xmlWriteSettings.colorSchema else ""
		c_r = xmlWriteSettings.colorSchema["r"] if xmlWriteSettings.colorSchema else ""
		c_t = xmlWriteSettings.colorSchema["t"] if xmlWriteSettings.colorSchema else ""

		text = htext.text
		if not text:
			return

		if xmlWriteSettings.textEncoding == EnumXMLTextOutputEncoding.AlwaysAsIs:
			w.write(
				c_t,
				text.replace("\n", "\n" + c_t),
				c_r
				)
		elif xmlWriteSettings.textEncoding == EnumXMLTextOutputEncoding.EncodeReservedCharsAsEntities:
			sb = [ c_t ]
			for c in text:
				if c == "\n":
					sb.append("\n" + c_t)
				elif c == "\"":
					sb.append("&quot")
				elif c == "&":
					sb.append("&amp")
				elif c == "<":
					sb.append("&lt")
				elif c == ">":
					sb.append("&gt")
				else:
					sb.append(c)
			sb.append(c_r)
			w.write(*sb)
		elif xmlWriteSettings.textEncoding == EnumXMLTextOutputEncoding.OnReservedCharsOutputTextAsCData:
			if ((text.find("&") >= 0) or (text.find("\"") >= 0) or (text.find(">") >= 0) or (text.find("<") >= 0)):
				w.write(
					c_t,
					"<![CDATA["
					)
				if text.find("<![CDATA[") >= 0:
					raise Exception("Text may not contain \"<![CDATA[\"! Recursive CDATA-definitions are not allowed!")
				w.write(
					text.replace("\n", "\n" + c_t),
					"]]>",
					c_r)
			else:
				w.write(
					c_t,
					text.replace("\n", "\n" + c_t),
					c_r
					)
		else:
			raise ImplementationErrorException("(None)" if xmlWriteSettings is None else str(xmlWriteSettings.textEncoding))
	#

	@staticmethod
	def __addXmlSingleLine(xmlWriteSettings:XMLWriteSettings, e:HElement, w:HWriter):
		if not e.children:
			HToolkit_Write_XML.__writeXmlOpeningClosingTag(xmlWriteSettings, e, w)
		else:
			HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
			for eChild in e.children:
				if isinstance(eChild, HText):
					HToolkit_Write_XML.__addXmlText(xmlWriteSettings, eChild, w)
				elif isinstance(eChild, HElement):
					HToolkit_Write_XML.__addXmlSingleLine(xmlWriteSettings, eChild, w)
				else:
					raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
			HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
	#

	@staticmethod
	def __addXmlSimple(xmlWriteSettings:XMLWriteSettings, e:HElement, bParentIsMixedContent:bool, w:HWriter):
		if not e.children:
			HToolkit_Write_XML.__writeXmlOpeningClosingTag(xmlWriteSettings, e, w)
			w.writeLn()
		else:
			if e.children.hasTexts:
				HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
				for eChild in e.children:
					if isinstance(eChild, HElement):
						HToolkit_Write_XML.__addXmlSimple(xmlWriteSettings, eChild, True, w)
					elif isinstance(eChild, HText):
						HToolkit_Write_XML.__addXmlText(xmlWriteSettings, eChild, w)
					else:
						raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
				HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
				if not bParentIsMixedContent:
					w.writeLn()

			else:
				HToolkit_Write_XML.__writeXmlOpeningTag(xmlWriteSettings, e, w)
				w.writeLn()
				for eChild in e.children:
					if isinstance(eChild, HElement):
						HToolkit_Write_XML.__addXmlSimple(xmlWriteSettings, eChild, False, w)
					else:
						raise ImplementationErrorException("(None)" if eChild is None else str(type(eChild)))
				HToolkit_Write_XML.__writeXmlClosingTag(xmlWriteSettings, e, w)
				w.writeLn()
	#

#










