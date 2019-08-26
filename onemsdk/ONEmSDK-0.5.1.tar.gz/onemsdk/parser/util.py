from html.parser import HTMLParser
from pathlib import Path
from typing import Union, TypeVar

import jinja2

from onemsdk.config import get_static_dir
from onemsdk.exceptions import MalformedHTMLException, ONEmSDKException
from onemsdk.parser.node import Node
from onemsdk.parser.tag import get_tag_cls, Tag

__all__ = ['load_html', 'load_template']


class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


StackT = TypeVar('StackT', bound=Stack)


class Parser(HTMLParser):
    def __init__(self):
        super(Parser, self).__init__()
        self.node: Union[Node, None] = None
        self.stack: StackT[Node] = Stack()

    def handle_starttag(self, tag, attrs):
        if self.node:
            raise Exception('Only one root tag permitted')

        tag_obj = Node(tag=tag, attrs=dict(attrs))

        if not self.stack.is_empty():
            last_tag_obj: Node = self.stack.peek()
            last_tag_obj.add_child(tag_obj)

        self.stack.push(tag_obj)

    def handle_endtag(self, tag):
        last_tag_obj: Node = self.stack.pop()

        if last_tag_obj.tag != tag:
            raise MalformedHTMLException(
                f'<{last_tag_obj.tag}> is the last opened tag, '
                f'but </{tag}> was received.'
            )

        if self.stack.is_empty():
            self.node = last_tag_obj

    def handle_startendtag(self, tag, attrs):
        tag_obj = Node(tag=tag, attrs=dict(attrs))
        last_tag_obj: Node = self.stack.peek()
        last_tag_obj.add_child(tag_obj)

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        data_bits = data.split()
        data = ' '.join(data_bits)
        last_tag_obj: Node = self.stack.peek()
        last_tag_obj.add_child(data)


def build_node(html: str) -> Node:
    parser = Parser()
    parser.feed(html)
    if not parser.stack.is_empty():
        raise MalformedHTMLException()
    return parser.node


def load_html(*, html_file: str = None, html_str: str = None) -> Tag:
    if html_file:
        html_file_path = Path(html_file)
        if not html_file_path.is_absolute():
            static_dir = get_static_dir()

            if static_dir:
                html_file_path = Path(static_dir).joinpath(html_file_path)

        with open(str(html_file_path), 'r') as f:
            html_str = f.read()

    node = build_node(html_str)
    tag_cls = get_tag_cls(node.tag)
    return tag_cls.from_node(node)


_jinja_env = None


def _load_template(template_file: str, **data) -> str:
    global _jinja_env

    template_file_path = Path(template_file)
    static_dir = get_static_dir()

    if not _jinja_env and static_dir:
        _jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(static_dir))
        )

    if _jinja_env:
        return _jinja_env.get_template(template_file).render(data)

    static_dir_ = str(template_file_path.parent.absolute())

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(static_dir_)
    ).get_template(template_file_path.name).render(data)


def load_template(template_file: str, **data) -> Tag:
    return load_html(html_str=_load_template(template_file, **data))
