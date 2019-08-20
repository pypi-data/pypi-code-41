# coding: utf-8

"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 10.0.0-dev.3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from flywheel.api_client import ApiClient
import flywheel.models

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

class DataexplorerApi(object):
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def get_search_query_suggestions(self, body, **kwargs):  # noqa: E501
        """Get suggestions for a structured search query

        Send the search query from the start of the string, and get a set of suggested replacements back. When utilizing a suggestion, the caller should replace the contents from the \"from\" field to the end of the string with the provided \"value\". 
        This method makes a synchronous HTTP request by default.

        :param SearchStructuredSearchQuery body: (required)
        :param bool async_: Perform the request asynchronously
        :return: SearchQuerySuggestions
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.get_search_query_suggestions_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.get_search_query_suggestions_with_http_info(body, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def get_search_query_suggestions_with_http_info(self, body, **kwargs):  # noqa: E501
        """Get suggestions for a structured search query

        Send the search query from the start of the string, and get a set of suggested replacements back. When utilizing a suggestion, the caller should replace the contents from the \"from\" field to the end of the string with the provided \"value\". 
        This method makes a synchronous HTTP request by default.

        :param SearchStructuredSearchQuery body: (required)
        :param bool async: Perform the request asynchronously
        :return: SearchQuerySuggestions
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('_request_out')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_search_query_suggestions" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `get_search_query_suggestions`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = flywheel.models.SearchStructuredSearchQuery.positional_to_model(params['body'])
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/dataexplorer/search/suggest', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='SearchQuerySuggestions',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def get_search_status(self, **kwargs):  # noqa: E501
        """Get the status of search (Mongo Connector)

        This method makes a synchronous HTTP request by default.

        :param bool async_: Perform the request asynchronously
        :return: SearchStatus
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.get_search_status_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_search_status_with_http_info(**kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def get_search_status_with_http_info(self, **kwargs):  # noqa: E501
        """Get the status of search (Mongo Connector)

        This method makes a synchronous HTTP request by default.

        :param bool async: Perform the request asynchronously
        :return: SearchStatus
        """

        all_params = []  # noqa: E501
        all_params.append('async_')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('_request_out')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_search_status" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/dataexplorer/search/status', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='SearchStatus',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def parse_search_query(self, body, **kwargs):  # noqa: E501
        """Parse a structured search query

        Validates a search query, returning any parse errors that were encountered. In the future, this endpoint may return the abstract syntax tree or evaluated query. 
        This method makes a synchronous HTTP request by default.

        :param SearchStructuredSearchQuery body: (required)
        :param bool async_: Perform the request asynchronously
        :return: SearchParseSearchQueryResult
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.parse_search_query_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.parse_search_query_with_http_info(body, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def parse_search_query_with_http_info(self, body, **kwargs):  # noqa: E501
        """Parse a structured search query

        Validates a search query, returning any parse errors that were encountered. In the future, this endpoint may return the abstract syntax tree or evaluated query. 
        This method makes a synchronous HTTP request by default.

        :param SearchStructuredSearchQuery body: (required)
        :param bool async: Perform the request asynchronously
        :return: SearchParseSearchQueryResult
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('_request_out')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method parse_search_query" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `parse_search_query`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = flywheel.models.SearchStructuredSearchQuery.positional_to_model(params['body'])
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/dataexplorer/search/parse', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='SearchParseSearchQueryResult',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def search(self, body, **kwargs):  # noqa: E501
        """Perform a search query

        This method makes a synchronous HTTP request by default.

        :param SearchQuery body: (required)
        :param bool simple:
        :param int size:
        :param bool async_: Perform the request asynchronously
        :return: list[SearchResponse]
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.search_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.search_with_http_info(body, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def search_with_http_info(self, body, **kwargs):  # noqa: E501
        """Perform a search query

        This method makes a synchronous HTTP request by default.

        :param SearchQuery body: (required)
        :param bool simple:
        :param int size:
        :param bool async: Perform the request asynchronously
        :return: list[SearchResponse]
        """

        all_params = ['body', 'simple', 'size']  # noqa: E501
        all_params.append('async_')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')
        all_params.append('_request_out')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method search" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `search`")  # noqa: E501

        if 'size' in params and params['size'] < 1:  # noqa: E501
            raise ValueError("Invalid value for parameter `size` when calling `search`, must be a value greater than or equal to `1`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'simple' in params:
            query_params.append(('simple', params['simple']))  # noqa: E501
        else:
            query_params.append(('simple', 'true'))
        if 'size' in params:
            query_params.append(('size', params['size']))  # noqa: E501
        else:
            query_params.append(('size', '100'))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = flywheel.models.SearchQuery.positional_to_model(params['body'])
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/dataexplorer/search', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[SearchResponse]',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)
