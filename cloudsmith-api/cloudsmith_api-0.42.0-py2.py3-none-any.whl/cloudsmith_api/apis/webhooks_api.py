# coding: utf-8

"""
    Cloudsmith API

    The API to the Cloudsmith Service

    OpenAPI spec version: v1
    Contact: support@cloudsmith.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class WebhooksApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def webhooks_create(self, owner, repo, **kwargs):
        """
        Create a specific webhook in a repository.
        Create a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_create(owner, repo, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param WebhooksCreate data:
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.webhooks_create_with_http_info(owner, repo, **kwargs)
        else:
            (data) = self.webhooks_create_with_http_info(owner, repo, **kwargs)
            return data

    def webhooks_create_with_http_info(self, owner, repo, **kwargs):
        """
        Create a specific webhook in a repository.
        Create a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_create_with_http_info(owner, repo, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param WebhooksCreate data:
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'repo', 'data']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method webhooks_create" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `webhooks_create`")
        # verify the required parameter 'repo' is set
        if ('repo' not in params) or (params['repo'] is None):
            raise ValueError("Missing the required parameter `repo` when calling `webhooks_create`")


        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'repo' in params:
            path_params['repo'] = params['repo']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'data' in params:
            body_params = params['data']
        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['apikey', 'csrf_token']

        return self.api_client.call_api('/webhooks/{owner}/{repo}/', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='RepositoryWebhook',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def webhooks_delete(self, owner, repo, identifier, **kwargs):
        """
        Delete a specific webhook in a repository.
        Delete a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_delete(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.webhooks_delete_with_http_info(owner, repo, identifier, **kwargs)
        else:
            (data) = self.webhooks_delete_with_http_info(owner, repo, identifier, **kwargs)
            return data

    def webhooks_delete_with_http_info(self, owner, repo, identifier, **kwargs):
        """
        Delete a specific webhook in a repository.
        Delete a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_delete_with_http_info(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'repo', 'identifier']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method webhooks_delete" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `webhooks_delete`")
        # verify the required parameter 'repo' is set
        if ('repo' not in params) or (params['repo'] is None):
            raise ValueError("Missing the required parameter `repo` when calling `webhooks_delete`")
        # verify the required parameter 'identifier' is set
        if ('identifier' not in params) or (params['identifier'] is None):
            raise ValueError("Missing the required parameter `identifier` when calling `webhooks_delete`")


        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'repo' in params:
            path_params['repo'] = params['repo']
        if 'identifier' in params:
            path_params['identifier'] = params['identifier']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['apikey', 'csrf_token']

        return self.api_client.call_api('/webhooks/{owner}/{repo}/{identifier}/', 'DELETE',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def webhooks_list(self, owner, repo, **kwargs):
        """
        Get a list of all webhooks in a repository.
        Get a list of all webhooks in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_list(owner, repo, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param int page: A page number within the paginated result set.
        :param int page_size: Number of results to return per page.
        :return: list[RepositoryWebhook]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.webhooks_list_with_http_info(owner, repo, **kwargs)
        else:
            (data) = self.webhooks_list_with_http_info(owner, repo, **kwargs)
            return data

    def webhooks_list_with_http_info(self, owner, repo, **kwargs):
        """
        Get a list of all webhooks in a repository.
        Get a list of all webhooks in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_list_with_http_info(owner, repo, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param int page: A page number within the paginated result set.
        :param int page_size: Number of results to return per page.
        :return: list[RepositoryWebhook]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'repo', 'page', 'page_size']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method webhooks_list" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `webhooks_list`")
        # verify the required parameter 'repo' is set
        if ('repo' not in params) or (params['repo'] is None):
            raise ValueError("Missing the required parameter `repo` when calling `webhooks_list`")


        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'repo' in params:
            path_params['repo'] = params['repo']

        query_params = []
        if 'page' in params:
            query_params.append(('page', params['page']))
        if 'page_size' in params:
            query_params.append(('page_size', params['page_size']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['apikey', 'csrf_token']

        return self.api_client.call_api('/webhooks/{owner}/{repo}/', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='list[RepositoryWebhook]',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def webhooks_partial_update(self, owner, repo, identifier, **kwargs):
        """
        Update a specific webhook in a repository.
        Update a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_partial_update(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :param WebhooksPartialUpdate data:
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.webhooks_partial_update_with_http_info(owner, repo, identifier, **kwargs)
        else:
            (data) = self.webhooks_partial_update_with_http_info(owner, repo, identifier, **kwargs)
            return data

    def webhooks_partial_update_with_http_info(self, owner, repo, identifier, **kwargs):
        """
        Update a specific webhook in a repository.
        Update a specific webhook in a repository.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_partial_update_with_http_info(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :param WebhooksPartialUpdate data:
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'repo', 'identifier', 'data']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method webhooks_partial_update" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `webhooks_partial_update`")
        # verify the required parameter 'repo' is set
        if ('repo' not in params) or (params['repo'] is None):
            raise ValueError("Missing the required parameter `repo` when calling `webhooks_partial_update`")
        # verify the required parameter 'identifier' is set
        if ('identifier' not in params) or (params['identifier'] is None):
            raise ValueError("Missing the required parameter `identifier` when calling `webhooks_partial_update`")


        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'repo' in params:
            path_params['repo'] = params['repo']
        if 'identifier' in params:
            path_params['identifier'] = params['identifier']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'data' in params:
            body_params = params['data']
        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['apikey', 'csrf_token']

        return self.api_client.call_api('/webhooks/{owner}/{repo}/{identifier}/', 'PATCH',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='RepositoryWebhook',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def webhooks_read(self, owner, repo, identifier, **kwargs):
        """
        Views for working with repository webhooks.
        Views for working with repository webhooks.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_read(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.webhooks_read_with_http_info(owner, repo, identifier, **kwargs)
        else:
            (data) = self.webhooks_read_with_http_info(owner, repo, identifier, **kwargs)
            return data

    def webhooks_read_with_http_info(self, owner, repo, identifier, **kwargs):
        """
        Views for working with repository webhooks.
        Views for working with repository webhooks.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.webhooks_read_with_http_info(owner, repo, identifier, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner:  (required)
        :param str repo:  (required)
        :param str identifier:  (required)
        :return: RepositoryWebhook
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'repo', 'identifier']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method webhooks_read" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `webhooks_read`")
        # verify the required parameter 'repo' is set
        if ('repo' not in params) or (params['repo'] is None):
            raise ValueError("Missing the required parameter `repo` when calling `webhooks_read`")
        # verify the required parameter 'identifier' is set
        if ('identifier' not in params) or (params['identifier'] is None):
            raise ValueError("Missing the required parameter `identifier` when calling `webhooks_read`")


        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'repo' in params:
            path_params['repo'] = params['repo']
        if 'identifier' in params:
            path_params['identifier'] = params['identifier']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['apikey', 'csrf_token']

        return self.api_client.call_api('/webhooks/{owner}/{repo}/{identifier}/', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='RepositoryWebhook',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
