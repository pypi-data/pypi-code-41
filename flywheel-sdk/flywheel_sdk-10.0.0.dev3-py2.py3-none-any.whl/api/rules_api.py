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

class RulesApi(object):
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def add_site_rule(self, body, **kwargs):  # noqa: E501
        """Create a new site rule.

        This method makes a synchronous HTTP request by default.

        :param Rule body: (required)
        :param bool async_: Perform the request asynchronously
        :return: None
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.add_site_rule_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.add_site_rule_with_http_info(body, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def add_site_rule_with_http_info(self, body, **kwargs):  # noqa: E501
        """Create a new site rule.

        This method makes a synchronous HTTP request by default.

        :param Rule body: (required)
        :param bool async: Perform the request asynchronously
        :return: None
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
                    " to method add_site_rule" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `add_site_rule`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = flywheel.models.Rule.positional_to_model(params['body'])
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/site/rules', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def get_site_rule(self, rule_id, **kwargs):  # noqa: E501
        """Get a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param bool async_: Perform the request asynchronously
        :return: Rule
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.get_site_rule_with_http_info(rule_id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_site_rule_with_http_info(rule_id, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def get_site_rule_with_http_info(self, rule_id, **kwargs):  # noqa: E501
        """Get a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param bool async: Perform the request asynchronously
        :return: Rule
        """

        all_params = ['rule_id']  # noqa: E501
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
                    " to method get_site_rule" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'rule_id' is set
        if ('rule_id' not in params or
                params['rule_id'] is None):
            raise ValueError("Missing the required parameter `rule_id` when calling `get_site_rule`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'rule_id' in params:
            path_params['RuleId'] = params['rule_id']  # noqa: E501

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
            '/site/rules/{RuleId}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Rule',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def get_site_rules(self, **kwargs):  # noqa: E501
        """List all site rules.

        This method makes a synchronous HTTP request by default.

        :param bool async_: Perform the request asynchronously
        :return: list[Rule]
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.get_site_rules_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_site_rules_with_http_info(**kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def get_site_rules_with_http_info(self, **kwargs):  # noqa: E501
        """List all site rules.

        This method makes a synchronous HTTP request by default.

        :param bool async: Perform the request asynchronously
        :return: list[Rule]
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
                    " to method get_site_rules" % key
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
            '/site/rules', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[Rule]',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def modify_site_rule(self, rule_id, body, **kwargs):  # noqa: E501
        """Update a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param Rule body: (required)
        :param bool async_: Perform the request asynchronously
        :return: None
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.modify_site_rule_with_http_info(rule_id, body, **kwargs)  # noqa: E501
        else:
            (data) = self.modify_site_rule_with_http_info(rule_id, body, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def modify_site_rule_with_http_info(self, rule_id, body, **kwargs):  # noqa: E501
        """Update a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param Rule body: (required)
        :param bool async: Perform the request asynchronously
        :return: None
        """

        all_params = ['rule_id', 'body']  # noqa: E501
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
                    " to method modify_site_rule" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'rule_id' is set
        if ('rule_id' not in params or
                params['rule_id'] is None):
            raise ValueError("Missing the required parameter `rule_id` when calling `modify_site_rule`")  # noqa: E501
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `modify_site_rule`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'rule_id' in params:
            path_params['RuleId'] = params['rule_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = flywheel.models.Rule.positional_to_model(params['body'])
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['ApiKey']  # noqa: E501

        return self.api_client.call_api(
            '/site/rules/{RuleId}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)

    def remove_site_rule(self, rule_id, **kwargs):  # noqa: E501
        """Remove a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param bool async_: Perform the request asynchronously
        :return: InlineResponse2002
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_'):
            return self.remove_site_rule_with_http_info(rule_id, **kwargs)  # noqa: E501
        else:
            (data) = self.remove_site_rule_with_http_info(rule_id, **kwargs)  # noqa: E501
            if data and hasattr(data, 'return_value'):
                return data.return_value()
            return data


    def remove_site_rule_with_http_info(self, rule_id, **kwargs):  # noqa: E501
        """Remove a site rule.

        This method makes a synchronous HTTP request by default.

        :param str rule_id: (required)
        :param bool async: Perform the request asynchronously
        :return: InlineResponse2002
        """

        all_params = ['rule_id']  # noqa: E501
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
                    " to method remove_site_rule" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'rule_id' is set
        if ('rule_id' not in params or
                params['rule_id'] is None):
            raise ValueError("Missing the required parameter `rule_id` when calling `remove_site_rule`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'rule_id' in params:
            path_params['RuleId'] = params['rule_id']  # noqa: E501

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
            '/site/rules/{RuleId}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='InlineResponse2002',  # noqa: E501
            auth_settings=auth_settings,
            async_=params.get('async_'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            _request_out=params.get('_request_out'),
            collection_formats=collection_formats)
