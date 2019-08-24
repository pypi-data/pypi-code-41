import re
from typing import Tuple, Optional, Iterator, List, Match

import markdown as md
from markdown import treeprocessors, postprocessors, preprocessors, inlinepatterns, util
from markdown.util import etree

PAGE_PAGEBREAK_PATTERN = re.compile(r'^\\pagebreak(Num)?$')
PAGE_PAGEBREAK_NUM_PATTERN = re.compile(r'^\\pagebreakNum$')

SECTION_HEADER_TAG_PATTERN = re.compile(r'^h[1-6]$')

COLUMN_COLUMNBREAK_PATTERN = re.compile(r'<p>\\columnbreak</p>')

STYLE_OPEN_PATTERN = re.compile(r'^\s*<style>')
STYLE_CLOSE_PATTERN = re.compile(r'</style>$')
STYLE_FULL_PATTERN = re.compile(r'^\s*<style>(.*)</style>$')
STYLE_EMPTY_LINE_PATTERN = re.compile(r'^\s*$')

DIV_OPEN_PATTERN = re.compile(r'^<div\b')

ANCHOR_POINT_PATTERN = re.compile(r'^\[(.*?)\]:<>$')

TAG_OPEN_PATTERN = re.compile(r'^<[^/]')

TABLE_LINE_PATTERN = re.compile(r'^(> *)\|')

DEL_PATTERN_STR = r'(~~([^~]+)~~)'


class CoreExtension(md.Extension):
    def extendMarkdown(self, md_: md.Markdown) -> None:
        md_.preprocessors.register(AnchorPointPreprocessor(), 'dndmd_anchor_point', 125)
        md_.preprocessors.register(TagPreprocessor(), 'dndmd_tag', 120)
        md_.preprocessors.register(StylePreprocessor(), 'dndmd_style', 110)
        md_.preprocessors.register(DivPreprocessor(), 'dndmd_div', 100)
        md_.preprocessors.register(TablePreprocessor(), 'dndmd_table', 90)

        md_.inlinePatterns.register(StyleInlineProcessor(), 'dndmd_style', 20)
        md_.inlinePatterns.register(inlinepatterns.SimpleTagInlineProcessor(DEL_PATTERN_STR, 'del'), 'dndmd_del', 20)

        md_.treeprocessors.register(PageNumTreeprocessor(), 'dndmd_page_num', 40)
        md_.treeprocessors.register(PageTreeprocessor(), 'dndmd_page', 30)
        md_.treeprocessors.register(SectionTreeprocessor(), 'dndmd_section', 20)
        md_.treeprocessors.register(SectionCleanupTreeprocessor(), 'dndmd_section_cleanup', 10)
        md_.treeprocessors.register(BlockquoteTreeprocessor(), 'dndmd_blockquote', 5)

        md_.postprocessors.register(ColumnPostprocessor(), 'dndmd_column', 20)


class AnchorPointPreprocessor(preprocessors.Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            match = ANCHOR_POINT_PATTERN.match(line)
            if match:
                anchor = etree.Element('a', {'name': match.group(1)})
                anchor.text = '__REPLACE_ME__'
                new_lines.append(etree.tostring(anchor, encoding='unicode').replace(anchor.text, ''))

        return new_lines


class TagPreprocessor(preprocessors.Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line in lines:
            if TAG_OPEN_PATTERN.match(line):
                new_lines.append('')
            new_lines.append(line)
        return new_lines


class StylePreprocessor(preprocessors.Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        in_style = False
        for line in lines:
            if not in_style and STYLE_OPEN_PATTERN.match(line):
                in_style = True
            if in_style and STYLE_EMPTY_LINE_PATTERN.fullmatch(line) is not None:
                continue
            if in_style and STYLE_CLOSE_PATTERN.search(line):
                in_style = False
            new_lines.append(line)
        return new_lines


class DivPreprocessor(preprocessors.Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        for line in lines:
            new_lines.append(DIV_OPEN_PATTERN.sub('<div markdown="1"', line))
        return new_lines


class TablePreprocessor(preprocessors.Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        new_lines = []
        prev_match = None
        for line in lines:
            match = TABLE_LINE_PATTERN.match(line)
            if prev_match is not None and match is None:
                new_lines.append(prev_match.group(1))
            new_lines.append(line)
            prev_match = match
        return new_lines


class StyleInlineProcessor(inlinepatterns.InlineProcessor):
    def __init__(self):
        super().__init__(STYLE_FULL_PATTERN.pattern, md)

    def handleMatch(self, m: Match, data: str) -> Tuple[etree.Element, int, int]:
        style = etree.Element('style')
        style.text = util.AtomicString(m.group(1))
        return style, 0, len(data)


class PageNumTreeprocessor(treeprocessors.Treeprocessor):
    def run(self, root: etree.Element) -> Optional[etree.Element]:
        for child in list(root):
            if child.tag == 'p' and child.text is not None and PAGE_PAGEBREAK_NUM_PATTERN.fullmatch(child.text):
                root.insert(list(root).index(child), etree.Element('div', {'class': 'pageNumber auto'}))
            self.run(child)
        return None


class PageTreeprocessor(treeprocessors.Treeprocessor):
    def run(self, root: etree.Element) -> Optional[etree.Element]:
        new_root = etree.Element(root.tag, root.attrib)
        while root is not None:
            root_head, root_tail = self._split_node(root)
            if root_head is None:
                root_head = root
            page = self._create_page()
            page.extend(list(root_head))
            new_root.append(page)
            root = root_tail
        return new_root

    @staticmethod
    def _create_page() -> etree.Element:
        return etree.Element('div', {'class': 'phb'})

    @staticmethod
    def _node_is_pagebreak(node: etree.Element) -> bool:
        return node.tag == 'p' and node.text is not None and PAGE_PAGEBREAK_PATTERN.fullmatch(node.text)

    def _split_node(self, node: etree.Element) -> Tuple[Optional[etree.Element], Optional[etree.Element]]:
        has_pagebreak = False

        head = etree.Element(node.tag, node.attrib)
        head.text = node.text

        tail = etree.Element(node.tag, node.attrib)
        tail.tail = node.tail

        for child in node:
            if has_pagebreak:
                tail.append(child)
                continue
            if self._node_is_pagebreak(child):
                has_pagebreak = True
                continue
            child_head, child_tail = self._split_node(child)
            if child_head is not None:
                has_pagebreak = True
                head.append(child_head)
                tail.append(child_tail)
                continue
            head.append(child)

        if has_pagebreak:
            return head, tail

        return None, None


class SectionTreeprocessor(treeprocessors.Treeprocessor):
    def run(self, root: etree.Element) -> Optional[etree.Element]:
        return self._run(root, 0)

    def _run(self, root: etree.Element, section_level: int) -> etree.Element:
        new_root = etree.Element(root.tag, root.attrib)
        new_root.text = root.text
        new_root.tail = root.tail
        iterator = iter(list(root))
        next_node = next(iterator, None)
        while next_node is not None:
            handled_node, next_node = self._handle_node(next_node, iterator, section_level)
            new_root.append(handled_node)
        return new_root

    def _handle_node(self, node: etree.Element, iterator: Iterator[Optional[etree.Element]], section_level: int) \
            -> Tuple[Optional[etree.Element], Optional[etree.Element]]:
        if node is None:
            return None, None
        header_level = self._header_level(node)
        if header_level <= section_level:
            return None, node
        if header_level < 7:
            subsection = self._create_section()
            next_node = next(iterator, None)
            while node is not None:
                subsection.append(node)
                node, next_node = self._handle_node(next_node, iterator, header_level)
            return subsection, next_node
        return self._run(node, 0), next(iterator, None)

    @staticmethod
    def _create_section() -> etree.Element:
        return etree.Element('section')

    @staticmethod
    def _header_level(node: etree.Element) -> int:
        if SECTION_HEADER_TAG_PATTERN.fullmatch(node.tag):
            return int(node.tag[1:])
        return 7


class SectionCleanupTreeprocessor(treeprocessors.Treeprocessor):
    def run(self, root: etree.Element) -> Optional[etree.Element]:
        self._cleanup_recursive(root)
        return None

    def _cleanup_recursive(self, node: etree.Element) -> None:
        for child in node:
            self._cleanup_recursive(child)
            if child.tag == 'section' \
                    and len(child) == 0 \
                    and (child.text is None or child.text.strip() == '') \
                    and (child.tail is None or child.tail.strip() == ''):
                node.remove(child)


class BlockquoteTreeprocessor(treeprocessors.Treeprocessor):
    def run(self, root: etree.Element) -> Optional[etree.Element]:
        self._run_recursive(root)
        return None

    def _run_recursive(self, node: etree.Element) -> None:
        for (i, child) in zip(range(len(node)), node):
            self._run_recursive(child)
            if child.tag == 'blockquote':
                new_child = etree.Element('section')
                new_child.append(child)
                node.remove(child)
                node.insert(i, new_child)


class ColumnPostprocessor(postprocessors.Postprocessor):
    def run(self, text: str) -> str:
        return COLUMN_COLUMNBREAK_PATTERN.sub('<div class="column-break"></div>', text)
