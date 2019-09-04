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

from website_python_client.api.api import RequestMethod, Api
from website_python_client.configuration import Configuration
from website_python_client.exceptions import ApiValueError, ApiNotFoundException
from website_python_client.models import Post


class PostApi(Api):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def create(self, post: Post, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        """create a new post

        :param bool sync:
        :param Post post: the post model
        :return: Post
        """
        self.accept = ['application/json']
        self.content_type = ['multipart/form-data']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/post', RequestMethod.POST, None, [],
                                  body=None, post_params=post.post_params(),
                                  files=[Post.upload_file(file) for file in post.file_params],
                                  _preload_content=post, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/post', RequestMethod.POST, None, [], None, post.post_params(),
                [Post.upload_file(file) for file in post.file_params], post, 300))

        return thread

    def delete(self, post: Union[Post, str], force: bool = False, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        """Delete the post by id

        :param sync:
        :param Post post: delete a post by this id (required)
        :param bool force: delete a post, force, by this id
        :return: Post
        """
        if not isinstance(post, Post):
            post = Post(post)

        query_params: List[Tuple[str, int]] = [('force', int(force))]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/post/{post}', RequestMethod.DELETE, [('post', post.identifier)], query_params,
                                  body=None, post_params=[], files=[], _preload_content=post, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, ('/post/{post}', RequestMethod.DELETE,
                                                            [('post', post.identifier)], query_params, None, [], [],
                                                            post, 300))

        return thread

    def list(self, page: int = 1, per_page: int = 100, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        """Returns all posts

        :param page:
        :param per_page:
        :param sync:
        :return:
        """
        if page < 1:
            raise ApiValueError(
                "Invalid value for parameter `per_page` when calling `list_post`," +
                " must be a value greater than or equal to `1`")

        if per_page < 1:
            raise ApiValueError(
                "Invalid value for parameter `page` when calling `list_post`," +
                "must be a value greater than or equal to `1`")

        query_params: List[Tuple[str, int]] = [
            ('page', page),
            ('perPage', per_page)
        ]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/post', RequestMethod.GET, None, query_params,
                                  body=None, post_params=[], files=[], _preload_content=Post, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/post', RequestMethod.GET, None, query_params, None, [], [], Post, 300))

        return thread

    def show(self, post: Union[Post, str], with_tags: bool = True, with_images: bool = True, foreign: bool = True,
             sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        """Returns a posts

        :param foreign:
        :param sync:
        :param Union[Post, str] post: get a post by this id (required)
        :param int with_tags: Show all Tags to this post?
        :param int with_images: Show all Images to this post?
        :return: Post
        """
        if not isinstance(post, Post):
            post = Post(post)

        query_params: List[Tuple[str, int]] = [
            ('withImages', int(with_tags)),
            ('withTags', int(with_images)),
            ('foreign', int(foreign))
        ]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/post/{post}', RequestMethod.GET, [('post', post.identifier)], query_params,
                                  body=None, post_params=[], files=[], _preload_content=post, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/post/{post}', RequestMethod.GET, [('post', post.identifier)], query_params, None, [], [], post, 300))

        return thread

    def show_or_create(self, post: Post, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.show(post, False, False, False, sync)
        except ApiNotFoundException:
            return self.create(post, sync)

    def update(self, post: Post, only: Optional[List[str]] = None, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        """ Update a post.

        :param Optional[List[str]] only:
        :param Post post:
        :param bool sync:
        :return Post:
        """

        self.accept = ['application/json']
        self.content_type = ['multipart/form-data']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/post/{post}', RequestMethod.PUT, [('post', post.identifier)], [],
                                  body=None, post_params=post.post_params(only),
                                  files=[Post.upload_file(file) for file in post.file_params],
                                  _preload_content=post, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/post/{post}', RequestMethod.PUT, [('post', post.identifier)], [], None, post.post_params(only),
                [Post.upload_file(file) for file in post.file_params], post, 300))

        return thread

    def update_or_create(self, post: Post, sync: bool = False) \
            -> Union[Tuple[Union[Post, List[Post], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.update(post, None, sync)
        except ApiNotFoundException:
            return self.create(post, sync)
