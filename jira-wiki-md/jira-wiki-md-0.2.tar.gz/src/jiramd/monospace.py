from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree, code_escape, AtomicString

MONOSPACE_PATTERN = r'\{\{(.+?)\}\}'


class MonospaceProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        pre = etree.Element('pre')
        pre.text = AtomicString(code_escape(m.group(1)))
        return pre, m.start(0), m.end(0)


monospace_processor = MonospaceProcessor(MONOSPACE_PATTERN)
