

from .HTMLElement import HTMLElement
from .htmlgeneral import *




class _HTMLElementProto(object):

	def __init__(self, name:str, bHasClosingTag=True, tagType=HTML_TAG_TYPE_INLINE_CONTENT, implClass=HTMLElement, extraAttributes:dict=None):
		assert isinstance(name, str)
		assert isinstance(bHasClosingTag, bool)

		self.name = name
		self.bHasClosingTag = bHasClosingTag
		self.tagType = tagType
		self.implClass = implClass

		if tagType == HTML_TAG_TYPE_INLINE_CONTENT:
			self.bLineBreakOuter = True
			self.bLineBreakInner = False
		elif tagType == HTML_TAG_TYPE_INLINE_ALL:
			self.bLineBreakOuter = False
			self.bLineBreakInner = False
		elif tagType == HTML_TAG_TYPE_STRUCTURE:
			self.bLineBreakOuter = True
			self.bLineBreakInner = True
		else:
			raise Exception("Invalid tag type specified: " + str(tagType))

		if extraAttributes:
			assert isinstance(extraAttributes, dict)
			self.extraAttributes = extraAttributes
		else:
			self.extraAttributes = None
	#

	def __call__(self, *args, **attrs):
		if self.extraAttributes:
			d = dict(self.extraAttributes)
			d.update(attrs)
			return self.implClass(self, self.name)(**d)
		else:
			return self.implClass(self, self.name)(**attrs)
	#

	def __getitem__(self, children):
		return self.implClass(self, self.name)[children]
	#

#







