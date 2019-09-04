# coding: utf-8

"""
    Felix' Website mit Blog
    The api of my blog.

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

from multiprocessing.pool import AsyncResult
from typing import Union, List, Tuple, Optional

from urllib3._collections import HTTPHeaderDict

from website_python_client.models.tag import Tag

from website_python_client.configuration import Configuration

from website_python_client.api.api import Api, RequestMethod
from website_python_client.exceptions import ApiValueError, ApiNotFoundException


class TagApi(Api):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def create(self, tag: Tag, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        """create a new tag

        :param bool sync:.
        :param Tag tag: The tag
        :return: Tag
                 If the method is called asynchronously,
                 returns the request thread.
        """
        self.accept = ['application/json']
        self.content_type = ['application/x-www-form-urlencoded']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/tag', RequestMethod.POST, None, [],
                                  body=None, post_params=tag.post_params(), files=[],
                                  _preload_content=tag, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/tag', RequestMethod.POST, None, [], None, tag.post_params(), [], tag, 300))

        return thread

    def delete(self, tag: Union[Tag, str], sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        """delete a tag

        :param bool sync:
        :param Tag tag: delete a tag by this id (required)
        :return: Tag
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if not isinstance(tag, Tag):
            tag = Tag(tag)

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/tag/{tag}', RequestMethod.DELETE, [('tag', tag.slug)], None,
                                  body=None, post_params=[], files=[], _preload_content=tag, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, ('/tag/{tag}', RequestMethod.DELETE,
                                                            [('tag', tag.slug)], None, None, [], [], tag, 300))

            return thread

    def show(self, tag: Union[Tag, str], foreign: bool = True, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        """get a tag

        :param bool sync:
        :param Tag tag: show a tag by this id (required)
        :param bool foreign: with all foreign keys
        :return: Tag
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if not isinstance(tag, Tag):
            tag = Tag(tag)

        query_params: List[Tuple[str, int]] = [
            ('morphForeign', int(foreign))
        ]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/tag/{tag}', RequestMethod.GET, [('tag', tag.slug)], query_params,
                                  body=None, post_params=[], files=[], _preload_content=tag, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/tag/{tag}', RequestMethod.GET, [('tag', tag.slug)], query_params, None, [], [], tag, 300))

        return thread

    def show_or_create(self, tag: Tag, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.show(tag, False, sync)
        except ApiNotFoundException:
            return self.create(tag, sync)

    def list(self, slug: Optional[str] = None, page: int = 1, per_page: int = 100, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        """Returned all tags

        :param str slug:
        :param int per_page:
        :param int page:
        :param bool sync:
        :return: list[Tag]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if page < 1:
            raise ApiValueError('The page number must be greater than 1.')

        if per_page < 1:
            raise ApiValueError('The files per page must be greater than 1.')

        query_params: List[Tuple[str, Union[str, int]]] = [
            ('page', page),
            ('perPage', per_page)
        ]

        if slug is not None:
            query_params.append(('slug', slug))

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/tag', RequestMethod.GET, None, query_params,
                                  body=None, post_params=[], files=[], _preload_content=Tag, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/tag', RequestMethod.GET, None, query_params, None, [], [], Tag, 300))

        return thread

    def update(self, tag: Tag, only: Optional[List[str]] = None, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        """update a tag

        :param bool sync:
        :param Tag tag: update a tag by this id (required)
        :param Optional[List[str]] only:
        :return: Tag
                 If the method is called asynchronously,
                 returns the request thread.
        """
        self.accept = ['application/json']
        self.content_type = ['application/x-www-form-urlencoded']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/tag/{tag}', RequestMethod.PUT, [('tag', tag.id if 'slug' in only else tag.slug)],
                                  [], body=None, post_params=tag.post_params(only), files=[],
                                  _preload_content=tag, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/tag/{tag}', RequestMethod.PUT, [('tag', tag.id if 'slug' in only else tag.slug)], [], None,
                tag.post_params(only), [], tag, 300))

        return thread

    def update_or_create(self, tag: Tag, sync: bool = False) \
            -> Union[Tuple[Union[Tag, List[Tag], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.update(tag, None, sync)
        except ApiNotFoundException:
            return self.create(tag, sync)
