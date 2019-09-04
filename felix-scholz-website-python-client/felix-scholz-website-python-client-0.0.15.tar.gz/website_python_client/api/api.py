# coding: utf-8

"""
    Felix' Website mit Blog
    The api of my blog.

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import
import json
import ssl

import certifi
from urllib3._collections import HTTPHeaderDict
from urllib3.exceptions import SSLError
from urllib3 import Timeout, ProxyManager, PoolManager
from enum import Enum
from multiprocessing.pool import ThreadPool
import re
from typing import NoReturn, Optional, List, Tuple, Any, Union

from six.moves.urllib.parse import quote, urlencode
from website_python_client.models.tag import Tag

from website_python_client.models.file import File

from website_python_client.models.category import Category

from website_python_client.models.post import Post

from website_python_client.api.rest_response import RESTResponse
from website_python_client.configuration import Configuration
from website_python_client.models.model import Model
from website_python_client.exceptions import ApiValueError, ApiException, ApiNotFoundException


class RequestMethod(Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


class Api(object):
    __pool = None

    def __init__(self, configuration: Configuration, pools_size: int = 4):
        self.configuration = configuration

        self.header_params: dict = {}
        self.user_agent = 'felix-scholz/website-python-client/1.0.1/python'

        addition_pool_args = {}
        if configuration.assert_hostname is not None:
            addition_pool_args['assert_hostname'] = configuration.assert_hostname

        if configuration.retries is not None:
            addition_pool_args['retries'] = configuration.retries

        if configuration.proxy:
            self.pool_manager = ProxyManager(
                num_pools=pools_size,
                maxsize=configuration.connection_pool_maxsize if not None else 4,
                cert_reqs=ssl.CERT_REQUIRED if configuration.verify_ssl else ssl.CERT_NONE,
                ca_certs=configuration.ssl_ca_cert if configuration.ssl_ca_cert is not None else certifi.where(),
                cert_file=configuration.cert_file,
                key_file=configuration.key_file,
                proxy_url=configuration.proxy,
                proxy_headers=configuration.proxy_headers,
                **addition_pool_args
            )
        else:
            self.pool_manager = PoolManager(
                num_pools=pools_size,
                maxsize=configuration.connection_pool_maxsize if not None else 4,
                cert_reqs=ssl.CERT_REQUIRED if configuration.verify_ssl else ssl.CERT_NONE,
                ca_certs=configuration.ssl_ca_cert if configuration.ssl_ca_cert is not None else certifi.where(),
                cert_file=configuration.cert_file,
                key_file=configuration.key_file,
                **addition_pool_args
            )

    def __del__(self):
        if self.__pool:
            self.__pool.close()
            self.__pool.join()
            self.__pool = None

    @property
    def pool(self) -> ThreadPool:
        if self.__pool is None:
            self.__pool = ThreadPool(self.configuration.pool_threads)

        return self.__pool

    @property
    def user_agent(self) -> dict:
        return self.header_params['User-Agent']

    @user_agent.setter
    def user_agent(self, value: str) -> NoReturn:
        self.header_params['User-Agent'] = value

    @property
    def x_debug(self) -> Optional[str]:
        if 'Cookie' in self.header_params:
            matches = re.match(r'XDEBUG_SESSION=(?P<name>\w+)', self.header_params['Cookie'])
            if matches is not None:
                return matches.group('name')

        return None

    @x_debug.setter
    def x_debug(self, session: str) -> NoReturn:
        if 'Cookie' not in self.header_params:
            self.header_params['Cookie'] = 'XDEBUG_SESSION=' + session
        elif self.x_debug is None:
            cookies = self.header_params['Cookie'].split(';')
            self.header_params['Cookie'] = ';'.join(cookies + ['XDEBUG_SESSION=' + session])

    @x_debug.deleter
    def x_debug(self) -> NoReturn:
        if 'Cookie' in self.header_params and self.x_debug is not None:
            self.header_params['Cookie'] = re.sub(r'XDEBUG_SESSION=(?P<name>\w+)', '', self.header_params['Cookie'])
            self.header_params['Cookie'].strip('; ')

    @property
    def accept(self) -> str:
        return self.header_params['Accept']

    @accept.setter
    def accept(self, accepts: List[str]) -> NoReturn:
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            self.header_params['Accept'] = 'application/json'
        else:
            self.header_params['Accept'] = ', '.join(accepts)

    @property
    def content_type(self) -> str:
        return self.header_params['Content-Type']

    @content_type.setter
    def content_type(self, content_types: List[str]) -> NoReturn:
        if not content_types:
            self.header_params['Content-Type'] = 'application/json'

        content_types = [x.lower() for x in content_types]

        if 'application/json' in content_types or '*/*' in content_types:
            self.header_params['Content-Type'] = 'application/json'
        else:
            self.header_params['Content-Type'] = content_types[0]

    def auth(self, authentications: List[str]) -> List[Tuple[str, str]]:
        queries: List[Tuple[str, str]] = []
        auth_settings = self.configuration.auth_settings()
        for auth_name in auth_settings.keys():
            if auth_name in authentications:
                if not auth_settings[auth_name]['value']:
                    continue
                elif auth_settings[auth_name]['in'] == 'header':
                    self.header_params[auth_settings[auth_name]['key']] = auth_settings[auth_name]['value']
                elif auth_settings[auth_name]['in'] == 'query':
                    queries.append((auth_settings[auth_name]['key'], auth_settings[auth_name]['value']))
            elif auth_settings[auth_name]['key'] in self.header_params:
                del self.header_params[auth_settings[auth_name]['key']]

        return queries

    def _call_api(
            self,
            resource_path: str,
            method: RequestMethod,
            path_params: Optional[List[Tuple[str, Union[int, str]]]],
            query_params: Optional[List[Tuple[Any, Any]]],
            body: Optional[Any],
            post_params: List[Tuple[str, Any]],
            files: List[Tuple[str, Tuple[str, bytes, str]]],
            _preload_content: Optional[Union[Model, type]] = None,
            _request_timeout: Optional[Union[Tuple[int, int], int]] = 300) \
            -> Tuple[Union[Model, List[Model], dict], int, HTTPHeaderDict]:

        if path_params is not None:
            for k, v in path_params:
                resource_path = resource_path.replace(
                    '{%s}' % k, quote(str(v), safe=self.configuration.safe_chars_for_path_param))

        post_params.extend(files)

        response_data = self.__request(
            method,
            self.configuration.host + resource_path,
            query_params=query_params,
            headers=self.header_params,
            post_params=post_params,
            body=body,
            _preload_content=True if _preload_content is not None else False,
            _request_timeout=_request_timeout)

        if _preload_content is not None:
            if type(_preload_content) in [Post, Category, File, Tag]:
                return _preload_content.deserialize(response_data), response_data.status, response_data.getheaders()
            elif _preload_content in [Post, Category, File, Tag]:
                return _preload_content.deserialize_all(response_data), response_data.status, response_data.getheaders()
        else:
            return json.loads(response_data)

    def __request(self,
                  method: RequestMethod,
                  url: str,
                  query_params=None,
                  headers=None,
                  body: Optional[Union[str, bytes, dict]] = None,
                  post_params: Optional[Any] = None,
                  _preload_content: bool = True,
                  _request_timeout: Optional[Union[Tuple[int, int], int]] = None) -> RESTResponse:
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param query_params: query parameters in the url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        if post_params is not None and body is not None:
            raise ApiValueError("body parameter cannot be used with post_params parameter.")

        post_params = post_params or {}
        headers = headers or {}

        timeout = None
        if _request_timeout:
            if isinstance(_request_timeout, int):
                timeout = Timeout(total=_request_timeout)
            elif (isinstance(_request_timeout, tuple) and
                  len(_request_timeout) == 2):
                timeout = Timeout(connect=_request_timeout[0], read=_request_timeout[1])

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        try:
            if method.value in ['POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']:
                if query_params:
                    url += '?' + urlencode(query_params)
                if re.search('json', headers['Content-Type'], re.IGNORECASE):
                    request_body = None
                    if body is not None:
                        request_body = json.dumps(body)
                    r = self.pool_manager.request(
                        method.value, url,
                        body=request_body,
                        preload_content=_preload_content,
                        timeout=timeout,
                        headers=headers)
                elif headers['Content-Type'] == 'application/x-www-form-urlencoded':  # noqa: E501
                    r = self.pool_manager.request(
                        method.value, url,
                        fields=post_params,
                        encode_multipart=False,
                        preload_content=_preload_content,
                        timeout=timeout,
                        headers=headers)
                elif headers['Content-Type'] == 'multipart/form-data':
                    # must del headers['Content-Type'], or the correct
                    # Content-Type which generated by urllib3 will be
                    # overwritten.
                    del headers['Content-Type']
                    r = self.pool_manager.request(
                        method.value, url,
                        fields=post_params,
                        encode_multipart=True,
                        preload_content=_preload_content,
                        timeout=timeout,
                        headers=headers)
                # Pass a `string` parameter directly in the body to support
                # other content types than Json when `body` argument is
                # provided in serialized form
                elif isinstance(body, str) or isinstance(body, bytes):
                    request_body = body
                    r = self.pool_manager.request(
                        method.value, url,
                        body=request_body,
                        preload_content=_preload_content,
                        timeout=timeout,
                        headers=headers)
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiException(status=0, reason=msg)
            # For `GET`, `HEAD`
            else:
                r = self.pool_manager.request(method.value, url,
                                              fields=query_params,
                                              preload_content=_preload_content,
                                              timeout=timeout,
                                              headers=headers)
        except SSLError as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            raise ApiException(status=0, reason=msg)

        if _preload_content:
            r = RESTResponse(r)

        if r.status == 404:
            raise ApiNotFoundException(http_resp=r)

        if not 200 <= r.status <= 299:
            raise ApiException(http_resp=r)

        return r
