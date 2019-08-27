from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree, code_escape, AtomicString

CODE_PATTERN = r'(\{code\})(.+?)\1'


class CodeProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        pre = etree.Element('pre')
        code = etree.SubElement(pre, 'code')
        code.text = AtomicString(code_escape(m.group(2)))
        return pre, m.start(0), m.end(0)


code_processor = CodeProcessor(CODE_PATTERN)
