# coding: utf-8

"""
    Felix' Website mit Blog
    The api of my blog.

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

from multiprocessing.pool import AsyncResult
from typing import Union, Tuple, List, Optional

from urllib3._collections import HTTPHeaderDict

from website_python_client.api.api import RequestMethod, Api
from website_python_client.models.file import File

from website_python_client.configuration import Configuration
from website_python_client.exceptions import ApiValueError, ApiNotFoundException


class FileApi(Api):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def create(self, file: Union[File, str], sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        """create a new file

        :param sync bool
        :param File file: The file content. (required)
        :return: File
        """
        self.accept = ['application/json']
        self.content_type = ['multipart/form-data']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/file', RequestMethod.POST, None, [],
                                  body=None, post_params=file.post_params(),
                                  files=[File.upload_file(file) for file in file.file_params()],
                                  _preload_content=file, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/file', RequestMethod.POST, None, [], None, file.post_params(),
                [File.upload_file(file) for file in file.file_params()], file, 300))

        return thread

    def delete(self, file: Union[File, str], sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        """Delete a file.

        :param bool sync:
        :param File file: Give the file id. (required)
        :return: File
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if not isinstance(file, File):
            file = File(file)

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/file/{file}', RequestMethod.DELETE, [('file', file.identifier)], None,
                                  body=None, post_params=[], files=[], _preload_content=file, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, ('/file/{file}', RequestMethod.DELETE,
                                                            [('file', file.identifier)], None, None, [], [],
                                                            file, 300))

        return thread

    def show(self, file: Union[File, str], foreign: bool = True, sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        """Get a File.

        :param bool sync:
        :param File file: Give the file id. (required)
        :param bool foreign: Resolve all foreign ids.
        :return: File
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if not isinstance(file, File):
            file = File(file)

        query_params: List[Tuple[str, int]] = [
            ('morphForeign', int(foreign))
        ]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/file/{file}', RequestMethod.GET, [('file', file.identifier)], query_params,
                                  body=None, post_params=[], files=[], _preload_content=file, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/file/{file}', RequestMethod.GET, [('file', file.identifier)], query_params, None, [], [], file, 300))

        return thread

    def show_or_create(self, file: File, sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.show(file, False, sync)
        except ApiNotFoundException:
            return self.create(file, sync)

    def list(self, page: int = 1, per_page: int = 100, sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        """Returned all files

        :param int page:
        :param int per_page:
        :param bool sync:
        :return: Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        if page < 1:
            raise ApiValueError('The page number must be greater than 1.')

        if per_page < 1:
            raise ApiValueError('The files per page must be greater than 1.')

        query_params: List[Tuple[str, int]] = [
            ('page', page),
            ('perPage', per_page)
        ]

        self.accept = ['application/json']
        self.content_type = ['application/json']
        self.auth(['ApiSecurity', 'ApiReadSecurity'])

        if not sync:
            return self._call_api('/file', RequestMethod.GET, None, query_params,
                                  body=None, post_params=[], files=[], _preload_content=File, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/file', RequestMethod.GET, None, query_params, None, [], [], File, 300))

        return thread

    def update(self, file: File, only: Optional[List[str]] = None, sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        """Update a file.

        :param File file:
        :param List[str] only:
        :param bool sync:
        :return: File
                 If the method is called asynchronously,
                 returns the request thread.
        """
        self.accept = ['application/json']
        self.content_type = ['application/x-www-form-urlencoded']
        self.auth(['ApiSecurity', 'ApiWriteSecurity'])

        if not sync:
            return self._call_api('/file/{file}', RequestMethod.PUT, [('file', file.identifier)], [],
                                  body=None, post_params=file.post_params(only), files=[],
                                  _preload_content=file, _request_timeout=300)
        else:
            thread = self.pool.apply_async(self._call_api, (
                '/file/{file}', RequestMethod.PUT, [('file', file.identifier)], [], None,
                file.post_params(only), [], file, 300))

        return thread

    def update_or_create(self, file: File, sync: bool = False) \
            -> Union[Tuple[Union[File, List[File], dict], int, HTTPHeaderDict], AsyncResult]:
        try:
            return self.update(file, None, sync)
        except ApiNotFoundException:
            return self.create(file, sync)
