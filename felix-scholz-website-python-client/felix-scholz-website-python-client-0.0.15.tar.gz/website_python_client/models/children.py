# coding: utf-8

"""
    Felix' Website mit Blog

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

from typing import List, Union, NoReturn, TYPE_CHECKING

if TYPE_CHECKING:
    from website_python_client.models import Category
    from website_python_client.models import Post


class Children(object):
    def __init__(self):
        self.__categories: List[Union[str, 'Category']] = []
        self.__posts: List[Union[str, 'Post']] = []

    @property
    def posts(self) -> List[Union[str, 'Post']]:
        return self.__posts

    @posts.setter
    def posts(self, posts: List[Union[str, 'Post']]) -> NoReturn:
        self.__posts = posts

    @property
    def categories(self) -> List[Union[str, 'Category']]:
        return self.__categories

    @categories.setter
    def categories(self, categories: List[Union[str, 'Category']]) -> NoReturn:
        self.__categories = categories
