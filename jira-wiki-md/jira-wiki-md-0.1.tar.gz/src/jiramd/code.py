from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

CODE_PATTERN = r'(\{code\})(.+?)\1'


class CodePattern(InlineProcessor):
    def handleMatch(self, m, data):
        pre = etree.Element('pre')
        code = etree.SubElement(pre, 'code')
        code.text = m.group(2)
        return pre, m.start(0), m.end(0)


code_processor = CodePattern(CODE_PATTERN)
