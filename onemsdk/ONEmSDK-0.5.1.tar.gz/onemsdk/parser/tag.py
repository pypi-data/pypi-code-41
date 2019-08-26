from __future__ import annotations

import inspect
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union, Type, Optional, Dict, Any

from pydantic import BaseModel

from onemsdk.exceptions import NodeTagMismatchException, ONEmSDKException
from .node import Node

__all__ = ['Tag', 'HeaderTag', 'FooterTag', 'BrTag', 'UlTag', 'LiTag', 'FormTag',
           'SectionTag', 'InputTagAttrs', 'InputTag', 'FormTagAttrs', 'PTag', 'ATag',
           'ATagAttrs', 'get_tag_cls', 'SectionTagAttrs', 'LiTagAttrs', 'InputTagType']


class Tag(BaseModel, ABC):
    class Config:
        tag_name: str = None

    attrs: Any = None
    children: List[Union[Tag, str]] = []

    @abstractmethod
    def render(self) -> str:
        pass

    @classmethod
    def from_node(cls, node: Node) -> Tag:
        if node.tag != cls.Config.tag_name:
            raise NodeTagMismatchException(
                f'Expected tag <{cls.Config.tag_name}>, received <{node.tag}>')

        attrs = cls.get_attrs(node)
        children = []

        for node_child in node.children:
            if isinstance(node_child, str):
                children.append(node_child)
            else:
                child_tag_cls = get_tag_cls(node_child.tag)
                children.append(child_tag_cls.from_node(node_child))

        return cls(attrs=attrs, children=children)

    @classmethod
    def get_attrs(cls, node: Node):
        return None


class HeaderTag(Tag):
    class Config:
        tag_name = 'header'

    def __init__(self, children: List[str] = None, **data):
        children = children or []
        if len(children) > 1 or children and not isinstance(children[0], str):
            raise ONEmSDKException('<header> must have max 1 text child')
        super(HeaderTag, self).__init__(children=children)

    def render(self):
        if len(self.children) == 1:
            return self.children[0]
        return ''

    def data(self):
        return None


HeaderTag.update_forward_refs()


class FooterTag(Tag):
    class Config:
        tag_name = 'footer'

    def __init__(self, children: List[str] = None, **data):
        children = children or []
        if len(children) > 1 or children and not isinstance(children[0], str):
            raise ONEmSDKException('<footer> must have max 1 text child')
        super(FooterTag, self).__init__(children=children)

    def render(self):
        if len(self.children) == 1:
            return self.children[0]
        return ''

    def data(self):
        return None


FooterTag.update_forward_refs()


class InputTagType(str, Enum):
    text = 'text'
    date = 'date'
    datetime = 'datetime'


class InputTagAttrs(BaseModel):
    type: InputTagType


class InputTag(Tag):
    class Config:
        tag_name = 'input'

    attrs: InputTagAttrs

    def __init__(self, attrs: InputTagAttrs, **data):
        super(InputTag, self).__init__(attrs=attrs)

    @classmethod
    def get_attrs(cls, node: Node):
        return InputTagAttrs(type=node.attrs.get('type'))

    def render(self):
        return ''

    def data(self) -> Optional[Dict[str, str]]:
        return None


InputTag.update_forward_refs()


class LabelTag(Tag):
    class Config:
        tag_name = 'label'

    def __init__(self, children: List[str] = None, **data):
        children = children or []
        if len(children) > 1 or children and not isinstance(children[0], str):
            raise ONEmSDKException('<label> must have max 1 text child')
        super(LabelTag, self).__init__(children=children)

    def render(self):
        return self.children[0]


LabelTag.update_forward_refs()


class ATagAttrs(BaseModel):
    href: str
    method: Optional[str] = 'GET'


class ATag(Tag):
    class Config:
        tag_name: str = 'a'

    attrs: ATagAttrs

    def __init__(self, attrs: ATagAttrs, children: List[str]):
        if len(children) != 1 or not isinstance(children[0], str):
            raise ONEmSDKException('<a> must have 1 text child')
        super(ATag, self).__init__(attrs=attrs, children=children)

    @classmethod
    def get_attrs(cls, node: Node) -> ATagAttrs:
        return ATagAttrs(href=node.attrs.get('href'),
                         method=node.attrs.get('method') or 'GET')

    def render(self):
        return self.children[0]

    def data(self) -> Dict[str, str]:
        return {
            **self.attrs.dict(),
            'text': self.children[0]
        }


ATag.update_forward_refs()


class LiTagAttrs(BaseModel):
    value: Optional[str]


class LiTag(Tag):
    class Config:
        tag_name = 'li'

    attrs: LiTagAttrs

    def __init__(self, children: List[Union[ATag, str]], attrs: LiTagAttrs = None):
        if len(children) != 1 or not isinstance(children[0], (str, ATag)):
            raise ONEmSDKException('<li> must have 1 (text or <a>) child')

        if attrs is None:
            attrs = LiTagAttrs()

        super(LiTag, self).__init__(attrs=attrs, children=children)

    @classmethod
    def get_attrs(cls, node: Node):
        return LiTagAttrs(value=node.attrs.get('value'))

    def render(self):
        if isinstance(self.children[0], ATag):
            return self.children[0].render()
        return self.children[0]


LiTag.update_forward_refs()


class UlTag(Tag):
    class Config:
        tag_name = 'ul'

    def __init__(self, children: List[LiTag], **data):
        if not children or not isinstance(children[0], LiTag):
            raise ONEmSDKException('<ul> must have min 1 <li> child')
        super(UlTag, self).__init__(children=children)

    def render(self):
        return '\n'.join([child.render() for child in self.children])


UlTag.update_forward_refs()


class PTag(Tag):
    class Config:
        tag_name = 'p'

    def __init__(self, children: List[str] = None, **data):
        children = children or []
        if len(children) > 1 or children and not isinstance(children[0], str):
            raise ONEmSDKException('<p> must have max 1 text child')
        super(PTag, self).__init__(children=children)

    def render(self):
        if len(self.children) == 1:
            return self.children[0]
        return ''

    def data(self):
        return {
            'text': self.children[0],
            'href': None,
            'data': None
        }


PTag.update_forward_refs()


class BrTag(Tag):
    class Config:
        tag_name = 'br'

    def __init__(self, **data):
        super(BrTag, self).__init__()

    def render(self):
        return '\n'

    def data(self):
        return {
            'text': '\n',
            'data': None,
            'href': None
        }


BrTag.update_forward_refs()


class SectionTagAttrs(BaseModel):
    header: Optional[str]
    footer: Optional[str]
    name: Optional[str]
    auto_select: bool = False
    multi_select: bool = False
    numbered: bool = False


class SectionTag(Tag):
    class Config:
        tag_name = 'section'

    attrs: SectionTagAttrs

    def __init__(self, attrs: SectionTagAttrs = None, children: List = None):
        children = children or []
        allowed_children = (FooterTag, HeaderTag, UlTag, PTag,
                            InputTag, LabelTag, BrTag, str)

        for child in children:
            if not isinstance(child, allowed_children):
                raise ONEmSDKException(
                    f'<{child.Config.tag_name}> cannot be child for <section>')

        super(SectionTag, self).__init__(attrs=attrs, children=children)

    def render(self, exclude_header: bool = False, exclude_footer: bool = False):
        # Add a temporary \n for help
        rendered_children = ['\n']

        for child in self.children:
            if isinstance(child, HeaderTag) and exclude_header:
                # Do not include header
                continue
            if isinstance(child, FooterTag) and exclude_footer:
                # Do not include footer
                continue

            if isinstance(child, str):
                text = child
            else:
                text = child.render()

            if text:
                if isinstance(child, PTag) or isinstance(child, UlTag):
                    if rendered_children[-1] != '\n':
                        rendered_children.append('\n')
                    rendered_children.append(text)
                    rendered_children.append('\n')
                else:
                    rendered_children.append(text)

        if rendered_children[-1] == '\n':
            del rendered_children[-1]

        # Remove the temporary \n
        del rendered_children[0]

        return ''.join(rendered_children)

    @classmethod
    def get_attrs(cls, node: Node) -> SectionTagAttrs:
        return SectionTagAttrs(
            header=node.attrs.get('header'),
            footer=node.attrs.get('footer'),
            name=node.attrs.get('name'),
            # Note that boolean attributes in HTML are evaluated to True if they are
            # present (their actual value does not matter). They are evaluated to False
            # only when they are missing
            auto_select='auto-select' in node.attrs,
            multi_select='multi-select' in node.attrs,
            numbered='numbered' in node.attrs,
        )


SectionTag.update_forward_refs()


class FormTagAttrs(BaseModel):
    header: Optional[str]
    footer: Optional[str]
    action: str
    method: str = 'POST'

    completion_status_show: bool = False
    completion_status_in_header: bool = False
    confirmation_needed: bool = False


class FormTag(Tag):
    class Config:
        tag_name = 'form'

    attrs: FormTagAttrs
    children: List[SectionTag]

    def __init__(self, attrs: FormTagAttrs, children: List[SectionTag]):
        if not children:
            raise ONEmSDKException('<form> must have at least 1 child')
        for child in children:
            if not isinstance(child, SectionTag):
                raise ONEmSDKException('<form> can have only <section> children')
            if not child.attrs.name:
                raise ONEmSDKException('<form> can contain only named <section> tags. '
                                       'Please add a unique "name" attribute in each form '
                                       'section.')

        super(FormTag, self).__init__(attrs=attrs, children=children)

    @classmethod
    def get_attrs(cls, node: Node):
        return FormTagAttrs(
            header=node.attrs.get('header'),
            footer=node.attrs.get('footer'),
            action=node.attrs.get('action'),
            method=node.attrs.get('method') or 'POST',
            completion_status_show='completion-status-show' in node.attrs,
            completion_status_in_header='completion-status-in-header' in node.attrs,
            confirmation_needed='confirmation-needed' in node.attrs,
        )

    def render(self):
        return '\n'.join([child.render() for child in self.children])


FormTag.update_forward_refs()

_map_tag_cls = {}

for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and issubclass(obj, Tag):
        _map_tag_cls[obj.Config.tag_name] = obj


def get_tag_cls(tag_name: str) -> Type[Tag]:
    global _map_tag_cls

    try:
        return _map_tag_cls[tag_name]
    except KeyError:
        raise ONEmSDKException(f'Tag <{tag_name}> is not supported')
