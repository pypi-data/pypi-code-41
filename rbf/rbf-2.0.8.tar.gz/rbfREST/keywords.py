# -*- coding: utf-8 -*-

#  Copyright 2019-  DNB
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# For Python 2
from __future__ import unicode_literals
from __future__ import division
from io import open
from .compat import IS_PYTHON_2, STRING_TYPES

from pytz import utc
from tzlocal import get_localzone

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from json import dumps, loads
from os import path, getcwd

from flex.core import validate_api_call
from genson import SchemaBuilder
from jsonpath_ng.ext import parse as parse_jsonpath
from jsonschema import validate, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from requests import request as client
from requests.exceptions import SSLError, Timeout

if IS_PYTHON_2:
    from urlparse import parse_qsl, urljoin, urlparse
else:
    from urllib.parse import parse_qsl, urljoin, urlparse

from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

import os.path
import json
from jsonpath_rw import Index, Fields
from jsonpath_rw_ext import parse

from .schema_keywords import SCHEMA_KEYWORDS


class Keywords(object):

    def get_keyword_names(self):
        return [name for name in dir(self) if hasattr(getattr(self, name),
                                                      'robot_name')]

    ### Keywords start here

    

#    @keyword(name=None, tags=("Settings",))
#    def set_headers(self, headers):
#        """*Sets new request headers or updates the existing.*

#        ``headers``: The headers to add or update as a JSON object or a
#        dictionary.

#        *Examples*

#        | `Set Headers` | { "authorization": "Basic QWxhZGRpbjpPcGVuU2VzYW1"} |
#        | `Set Headers` | { "Accept-Encoding": "identity"} |
#        | `Set Headers` | ${auth_dict} |
#        """
#        self.request['headers'].update(self._input_object(headers))
#        return self.request['headers']

    

    

    

    

    @keyword(name=None, tags=("Requests",))
    def head(self, endpoint, headers=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends a HEAD request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s) 

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5 

        ``allow_redirects``: If true, follow all redirects.
        In contrary to other methods, no HEAD redirects are followed by default.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` will apply for `HEAD`.

        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "HEAD"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("Requests",))
    def options(self, endpoint, headers=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends an OPTIONS request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` will apply for `OPTIONS`.
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "OPTIONS"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("Requests",))
    def get(self, endpoint, headers=None, query=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends a GET request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``query``: Request query parameters as a JSON object or a dictionary.
        Alternatively, query parameters can be given as part of endpoint as well.

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

		``Set Headers:``
        | `GET` | https://jsonplaceholder.typicode.com/users   | headers={ "Authentication": "Basic ..", "Trace-Id": "1234" } | timeout=2.5 |

        ``Load Headers from JSON File:``
        | ${requestHeaders} |  `Load Headers`  | ${EXECDIR}/path/to/file.json |
        | `GET` | https://jsonplaceholder.typicode.com/users   | headers=${requestHeaders} | 

        ``Load Headers (as a template) from JSON file and Update values of headers:``
        | ${requestHeaders} |  `Load Headers`  | ${EXECDIR}/path/to/file.json |
        | ${updatedHeaders} |  `Update Header` | ${requestHeaders} |  X-DNBAPI-UserId  |  TBxxxxx |
        | `GET` | https://jsonplaceholder.typicode.com/users   | headers=${updatedHeaders} |

        ``Query Params:``       
        | `GET` | https://jsonplaceholder.typicode.com/users?_limit=2 |
        | `GET` | https://jsonplaceholder.typicode.com/users   | query={ "_limit": "2" } | #same as above |            

        ``Set Query Params :``
        | ${updatedEndpoint} | `Set Query Param` | https://testserver/v1/accounts | accountNumber | 12085214800 |
        | `GET` | ${updatedEndpoint} |

        ``Path Params:``
        | `GET` | https://jsonplaceholder.typicode.com/users/1   |

        ``Set Path Params:``
        | ${updatedEndpoint} | `Set Path Param` | https://jsonplaceholder.typicode.com/users/{id} | {id} | 1 |
        | `GET` | ${updatedEndpoint} |  
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "GET"
        request['query'] = OrderedDict()
        query_in_url = OrderedDict(parse_qsl(urlparse(endpoint).query))
        if query_in_url:
            request['query'].update(query_in_url)
            endpoint = endpoint.rsplit('?', 1)[0]
        if query:
            request['query'].update(self._input_object(query))
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']
        
        
    @keyword(name=None, tags=("Requests",))
    def post(self, endpoint, body=None, timeout=None, allow_redirects=None, validate=True, headers=None):
        """*Sends a POST request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``body``: Request body as a JSON object.

        Following keywords can be used :  
        - `Load Payload` to load default payload
        - `Update Payload` to update value of existing payload

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` will apply for `POST`. Below examples show usage of payload keywords

        ``POST request by passing payload manually``
        | `POST` | https://jsonplaceholder.typicode.com/users   | body={ "id": 11, "name": "Gil Alexander" } | 

        ``POST request by loading payload from a JSON file``
        | ${requestPayload} |  `Load Payload`  | ${EXECDIR}/path/to/file.json |
        | `POST` | https://jsonplaceholder.typicode.com/users   | body=${requestPayload} | 

        ``POST request by loading payload (as a template) from a JSON file and updating values of payload``
        | ${requestPayload} |  `Load Payload`  | ${EXECDIR}/path/to/file.json |
        | ${updatedPayload} |  `Update Payload` | ${requestPayload} |  name  |  Tom Cruise |
        | `POST` | https://jsonplaceholder.typicode.com/users   | body=${updatedPayload} |
        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "POST"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("Requests",))
    def put(self, endpoint, headers=None, body=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends a PUT request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``body``: Request body as a JSON object.

        Following keywords can be used :  
        - `Load Payload` to load default payload
        - `Update Payload` to update value of existing payload

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` & `POST` will apply for `PUT`


        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "PUT"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("Requests",))
    def patch(self, endpoint, headers=None, body=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends a PATCH request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``body``: Request body as a JSON object.

        Following keywords can be used :  
        - `Load Payload` to load default payload
        - `Update Payload` to update value of existing payload

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` & `POST` will apply for `PATCH`

        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "PATCH"
        request['body'] = self.input(body)
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    @keyword(name=None, tags=("Requests",))
    def delete(self, endpoint, headers=None, timeout=None, allow_redirects=None, validate=True):
        """*Sends a DELETE request to the endpoint.*

        *Arguments*

        ``endpoint``: REST API service endpoint URL - including resource path & query/path parameter(s)

        ``headers``: Headers as a JSON object to add or override for the request.

        Following keywords can be used :  
        - `Load Headers` to load default headers
        - `Add Headers` to add new headers
        - `Update Header` to update value of existing header

        ``timeout``: Number of seconds to wait for the response before failing the keyword. No timeout set by default. For ex: timeout=2.5

        ``allow_redirects``: If false, do not follow any redirects.

        ``validate``: If false, skips any request and response validations set by expectation keywords.

        *Examples*

        Examples of `GET` will apply for `DELETE`


        """
        endpoint = self._input_string(endpoint)
        request = deepcopy(self.request)
        request['method'] = "DELETE"
        if allow_redirects is not None:
            request['allowRedirects'] = self._input_boolean(allow_redirects)
        if timeout is not None:
            request['timeout'] = self._input_timeout(timeout)
        validate = self._input_boolean(validate)
        if headers:
            request['headers'].update(self._input_object(headers))
        return self._request(endpoint, request, validate)['response']

    
    
    def input(self, what):
        """*Converts the input to JSON and returns it.*
        Any of the following is accepted:
        - The path to JSON file
        - Any scalar that can be interpreted as JSON
        - A dictionary or a list
        *Examples*
        | ${payload} | `Input` | ${CURDIR}/payload.json |
        | ${object} | `Input` | { "name": "Julie Langford", "username": "jlangfor" } |
        | ${object} | `Input` | ${dict} |
        | ${array} | `Input` | ["name", "username"] |
        | ${array} | `Input` | ${list} |
        | ${boolean} | `Input` | true |
        | ${boolean} | `Input` | ${True} |
        | ${number} | `Input` | 2.0 |
        | ${number} | `Input` | ${2.0} |
        | ${string} | `Input` | Quotes are optional for strings |
        """
        if what is None:
            return None
        if not isinstance(what, STRING_TYPES):
            return self._input_json_from_non_string(what)
        if path.isfile(what):
            return self._input_json_from_file(what)
        try:
            return self._input_json_as_string(what)
        except ValueError:
            return self._input_string(what)    
        
    
    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_not_found(self, field, response=None):
        """*Asserts that the JSON field does not exist. Throws Assertion error if field is found*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

		``response``: Response object for validation 

        *Examples*

        | `GET`    | https://jsonplaceholder.typicode.com/users/1 |
        | `Assert If Field is Not Found` | response body password |
        | `Assert If Field is Not Found` | $.password |
        | `Assert If Field is Not Found` | $..geo.elevation | # JSONPath represention |
        | `Assert If Field is Not Found` | response body address geo elevation | # Same as above, fields seperated by spaces |

        | `GET`    | https://jsonplaceholder.typicode.com/users/1   |
        | `Assert If Field is Not Found` | response body 0 password |
        | `Assert If Field is Not Found` | $[*].password |
        | `Assert If Field is Not Found` | $[*]..geo.elevation |
        """
        try:
            matches = self._find_by_field(field, response, print_found=False)
        except AssertionError:
            return
        for found in matches:
            self.log_json(found['reality'],
                          "\n\nExpected '%s' to not exist, but it is:" % (field))
        raise AssertionError("Expected '%s' to not exist, but it does." % (
            field))

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_null(self, field, response=None, **validations):
        """*Asserts that the JSON field is null. Throws error if field is not null*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/generic.html|common for all types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  		   | https://jsonplaceholder.typicode.com/users/1 | { "deactivated_at": null } | |
        | `Assert If Field is Null` | response body deactivated_at | # JSONPath alternative |
        | `Assert If Field is Null` | $.deactivated_at | | |
        """
        values = []
        for found in self._find_by_field(field, response):
            reality = found['reality']
            schema = {"type": "null"}
            skip = self._input_boolean(validations.pop('skip', False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_boolean(self, field, response=None, value=None, **validations):
        """*Asserts that the JSON field is boolean.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``value``:

        If given, the property value is validated in addition to the type.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/generic.html|common for all types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  		      | https://jsonplaceholder.typicode.com/users/1 | { "verified_email": true } | | |  |
        | `Assert If Field is Boolean` | response body verified_email | | | | # value is optional |
        | `Assert If Field is Boolean` | response body verified_email | true | | | # JSONPath alternative |
        | `Assert If Field is Boolean` | response body verified_email | ${True} | | | # same as above |
        | `Assert If Field is Boolean` | $.verified_email | true | | | |
        | `Assert If Field is Boolean` | $.verified_email | true | enum=[1, "1"] | skip=true | # would pass |
        """
        values = []
        for found in self._find_by_field(field, response):
            reality = found['reality']
            schema = {"type": "boolean"}
            if value is not None:
                schema['enum'] = [self._input_boolean(value)]
            elif self._should_add_examples():
                schema['examples'] = [reality]
            skip = self._input_boolean(validations.pop('skip', False))
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_integer(self, field, *enum, response=None, **validations):
        """*Asserts that the JSON field is Integer.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``enum``:

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/numeric.html#integer|for numeric types]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `GET`  			  | https://jsonplaceholder.typicode.com/users/1 | |  |
        | `Assert If Field is Integer` | response body id | | # value is optional |
        | `Assert If Field is Integer` | response body id | 1 | # JSONPath alternative |
        | `Assert If Field is Integer` | response body id | ${1} | # same as above |
        | `Assert If Field is Integer` | $.id | 1 | |

        | `GET`  			  | https://jsonplaceholder.typicode.com/users?_limit=10 | | | | |
        | `Assert If Field is Integer` | response body 0 id | 1 | | |
        | `Assert If Field is Integer` | $[0].id | 1 | | | # same as above |
        | `Assert If Field is Integer` | $[*].id | | minimum=1 | maximum=10 |
        """
        values = []
        for found in self._find_by_field(field, response):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("integer", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_integer(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            elif self._should_add_examples():
                schema['examples'] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_number(self, field, *enum, response=None, **validations):
        """*Asserts that the JSON field is number.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``enum``:

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/numeric.html#number|for numeric types] can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `PUT`  | https://jsonplaceholder.typicode.com/users/1 | { "allocation": 95.0 } | |
        | `Number` | response body allocation | | # value is optional |
        | `Number` | response body allocation | 95.0 | # JSONPath alternative |
        | `Number` | response body allocation | ${95.0} | # same as above |
        | `Number` | $.allocation | 95.0 | # JSONPath representation |

        | `GET`  | https://jsonplaceholder.typicode.com/users?_limit=10 | | | | |
        | `Number` | $[0].id | 1 | | | # integers are also numbers |
        | `Number` | $[*].id | | minimum=1 | maximum=10 |
        """
        values = []
        for found in self._find_by_field(field, response):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("number", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_number(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            elif self._should_add_examples():
                schema['examples'] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values
        

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_string(self, field, *enum, response=None, **validations):
        """*Asserts that the JSON field is String.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``enum``:

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/string.html|for string]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.
      
        
        *Examples*

        | `GET`  			 | https://jsonplaceholder.typicode.com/users/1 | | | |
        | `Assert If Field is String` | response body email | | | # value is optional |
        | `Assert If Field is String` | response body email | Sincere@april.biz |
        | `Assert If Field is String` | $.email | Sincere@april.biz | | |
        | `Assert If Field is String` | $.email | | format=email |

        | `GET`  			 | https://jsonplaceholder.typicode.com/users?_limit=10 | | | |
        | `Assert If Field is String` | response body 0 email | Sincere@april.biz |
        | `Assert If Field is String` | $[0].email | Sincere@april.biz | | # same as above |
        | `Assert If Field is String` | $[*].email | | format=email |
        """
        values = []
        for found in self._find_by_field(field, response):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("string", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_string(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            elif self._should_add_examples():
                schema['examples'] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values       
         

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_object(self, field, *enum, response=None, **validations):
        """*Asserts that the JSON field is Object.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``enum``:

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/object.html|for object]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*

        | `GET`  			 | https://jsonplaceholder.typicode.com/users/1 | | |
        | `Assert If Field is Object` | response body | |
        | `Assert If Field is Object` | response body | required=["id", "name"] | # can have other properties |

        | `GET`  			 | https://jsonplaceholder.typicode.com/users/1 | | |
        | `Assert If Field is Object` | $.address.geo | required=["lat", "lng"] |
        | `Assert If Field is Object` | $..geo | additionalProperties=false | # cannot have other properties |
        """
        values = []
        for found in self._find_by_field(field, response):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("object", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_object(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            elif self._should_add_examples():
                schema['examples'] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

    @keyword(name=None, tags=("Assertions",))
    def assert_if_field_is_array(self, field, *enum, response=None, **validations):
        """*Asserts the JSON field is Array.*

        *Arguments*

        ``field``: 

        The field consists of parts separated by spaces, the parts being
        object property names or array indices starting from 0, and the root
        being the instance created by the last request (see `Output` for it).

        For asserting deeply nested properties or multiple objects at once,
        [http://goessner.net/articles/JsonPath|JSONPath] can be used with
        the root being the response body.

        ``response``: Response object for validation 
        
        ``enum``:

        The allowed values for the property as zero or more arguments.
        If none given, the value of the property is not asserted.

        ``validations``:

        The JSON Schema validation keywords
        [https://json-schema.org/understanding-json-schema/reference/array.html|for array]
        can be used. Validations are optional but update the schema of
        the property (more accurate) if given.
        `Output Schema` can be used for the current schema of the field.

        The keyword will fail if any of the given validations fail.
        Given validations can be skipped altogether by adding ``skip=true``.
        When skipped, the schema is updated but the validations are not ran.
        Skip is intented mainly for debugging the updated schema before aborting.

        *Examples*
        | `GET`  			| https://jsonplaceholder.typicode.com/users?_limit=10 | | | |
        | `Assert If Field is Array` | response body | | |
        | `Assert If Field is Array` | $ | # same as above | 
        | `Assert If Field is Array` | $ | minItems=1 | maxItems=10 | uniqueItems=true |
        """
        values = []
        for found in self._find_by_field(field, response):
            schema = found['schema']
            reality = found['reality']
            skip = self._input_boolean(validations.pop('skip', False))
            self._set_type_validations("array", schema, validations)
            if enum:
                if 'enum' not in schema:
                    schema['enum'] = []
                for value in enum:
                    value = self._input_array(value)
                    if value not in schema['enum']:
                        schema['enum'].append(value)
            elif self._should_add_examples():
                schema['examples'] = [reality]
            if not skip:
                self._assert_schema(schema, reality)
            values.append(reality)
        return values

#    @keyword(name=None, tags=("Settings",))
#    def convert_input_to_json(self, what):
#        """*Converts the input to JSON and returns it.*

#        Any of the following is accepted:

#        - The path to JSON file
#        - Any scalar that can be interpreted as JSON
#        - A dictionary or a list

#        *Examples*

#        | ${payload} | `Convert Input To JSON` | ${CURDIR}/payload.json |

#        | ${object} | `Convert Input To JSON` | { "name": "Julie Langford", "username": "jlangfor" } |
#        | ${object} | `Convert Input To JSON` | ${dict} |

#        | ${array} | `Convert Input To JSON` | ["name", "username"] |
#        | ${array} | `Convert Input To JSON` | ${list} |

#        | ${boolean} | `Convert Input To JSON` | true |
#        | ${boolean} | `Convert Input To JSON` | ${True} |

#        | ${number} | `Convert Input To JSON` | 2.0 |
#        | ${number} | `Convert Input To JSON` | ${2.0} |

#        | ${string} | `Convert Input To JSON` | Quotes are optional for strings |
#        """
#        if what is None:
#            return None
#        if not isinstance(what, STRING_TYPES):
#            return self._input_json_from_non_string(what)
#        if path.isfile(what):
#            return self._input_json_from_file(what)
#        try:
#            return self._input_json_as_string(what)
#        except ValueError:
#            return self._input_string(what)    

    

    @keyword(name=None, tags=("Logging",))
    def print(self, element="", file_path=None, append=False, sort_keys=False):
        """*Outputs the element as JSON to terminal or a file.*


        *Arguments*

        ``element``: By default, the last request and response are output to terminal.
        The output can be limited further by: 

        - The property of last instance, e.g. ``request`` or ``response``
        - Any nested property that exists, e.g. using JSONPath


        ``file_path``: The JSON is written to a file instead of terminal.
        The file is created if it does not exist.

        ``append``: If true, the JSON is appended to the given file
        instead of truncating it first.

        ``sort_keys``: If true, the JSON is sorted alphabetically by
        property names before it is output.

        *Examples*

        | `Print` | response | # only the response is output |
        | `Print` | response body | # only the response body is output |
        | `Print` | $.email | # only the response body property is output |
        | `Print` | $..geo | # only the nested response body property is output |

        | `Print` | request | # only the request is output |
        | `Print` | request headers | # only the request headers are output |
        | `Print` | request headers Authentication | # only this header is output |

        | `Print` | response body | ${CURDIR}/response_body.json | | # write the response body to a file |
        | `Print` | response seconds | ${CURDIR}/response_delays.log | append=true | # keep track of response delays in a file |
        """
        if isinstance(element, (STRING_TYPES)):
            if element == "":
                try:
                    json = deepcopy(self._last_instance_or_error())
                    json.pop('schema')
                    json.pop('spec')
                except IndexError:
                    raise RuntimeError(no_instances_error)
            elif element.startswith("schema"):
                logger.warn("Using `Output` for schema is deprecated. " +
                            "Using `Output Schema` to handle schema paths better.")
                element = element.lstrip("schema").lstrip()
                return self.output_schema(element, file_path, append, sort_keys)
            elif element.startswith(("request", "response", "$")):
                self._last_instance_or_error()
                matches = self._find_by_field(element, return_schema=False)
                if len(matches) > 1:
                    json = [found['reality'] for found in matches]
                else:
                    json = matches[0]['reality']
            else:
                try:
                    json = self._input_json_as_string(element)
                except ValueError:
                    json = self._input_string(element)
        else:
            json = self._input_json_from_non_string(element)
        sort_keys = self._input_boolean(sort_keys)
        if not file_path:
            self.log_json(json, sort_keys=sort_keys)
        else:
            content = dumps(json, ensure_ascii=False, indent=4,
                            separators=(',', ': '), sort_keys=sort_keys)
            write_mode = 'a' if self._input_boolean(append) else 'w'
            try:
                with open(path.join(getcwd(), file_path), write_mode,
                          encoding="utf-8") as file:
                    if IS_PYTHON_2:
                        content = unicode(content)
                    file.write(content)
            except IOError as e:
                raise RuntimeError("Error outputting to file '%s':\n%s" % (
                    file_path, e))
        return json

#    @keyword(name=None, tags=("Logging",))
#    def rest_instances(self, file_path=None, sort_keys=False):
#        """*Writes the instances as JSON to a file*

#        The instances are written to file as a JSON array of JSON objects,
#        each object representing a single instance, and having three properties:

#        - the request
#        - the response
#        - the schema for both, which have been updated according to the tests

#        The file is created if it does not exist, otherwise it is truncated.

#        *Arguments*

#        ``sort_keys``: If true, the instances are sorted alphabetically by
#        property names.

#        *Examples*

#        | `Rest Instances` | ${CURDIR}/log.json |
#        """
#        if not file_path:
#            outputdir_path = BuiltIn().get_variable_value("${OUTPUTDIR}")
#            if self.request['netloc']:
#                file_path = path.join(outputdir_path,
#                                      self.request['netloc']) + '.json'
#            else:
#                file_path = path.join(outputdir_path, "instances") + '.json'
#        sort_keys = self._input_boolean(sort_keys)
#        content = dumps(self.instances, ensure_ascii=False, indent=4,
#                        separators=(',', ': '), sort_keys=sort_keys)
#        try:
#            with open(file_path, 'w', encoding="utf-8") as file:
#                if IS_PYTHON_2:
#                    content = unicode(content)
#                file.write(content)
#        except IOError as e:
#            raise RuntimeError("Error exporting instances " +
#                               "to file '%s':\n%s" % (file_path, e))
#        return self.instances
        
    
    @keyword(name=None, tags=("Assertions",))
    def extract_response_for_assertions(self):
        """*Extracts the response into a variable that can further be used in assertions and value chain testing. Returns RESTInstance object that includes both request and response objects*

        *Examples*

        | ${response} | `Extract Response For Assertions` | 
        """
        return self.instances[-1]    

    

    @keyword(name=None, tags=("Settings",))
    def update_payload(self, request_payload, json_path, new_value):
        """*Update value to JSON payload using JSONPath. Returns updatedPayload as JSON object*

        *Arguments*

            ``request_payload``: json object

            ``json_path``: jsonpath expression

            ``new_value``: value to update

        *Examples*

        | ${updatedPayload}=  |  `Update Payload` | ${requestPayload} |  $..address.streetAddress  |  Ratchadapisek Road |
        """
        updated_payload = dict(request_payload)
        json_path_expr = parse(json_path)
        for match in json_path_expr.find(updated_payload):
            path = match.path
            if isinstance(path, Index):
                match.context.value[match.path.index] = new_value
            elif isinstance(path, Fields):
                match.context.value[match.path.fields[0]] = new_value
        return updated_payload

    @keyword(name=None, tags=("Settings",))
    def delete_header(self, request_headers, header_name):
        """*Delete a dictionary or list object from existing JSON header object. Returns updatedHeaders as JSON Object*

	    *Arguments*
	
	        ``request_headers``: json object
	
	        ``header_name``: Header to be deleted
	
	    *Examples*
	
	    | ${updatedHeaders}  |  `Delete Header` | ${requestHeaders} |  Authorization  |
	    """
        json_headers = self.input(request_headers)
        json_path_expr = parse('$' + '.' + header_name)
        matches = json_path_expr.find(json_headers)
        if not matches:
            raise AssertionError("Header '%s' " % (header_name) +
                             "did not match anything.")
        for match in json_path_expr.find(json_headers):
	        path = match.path
	        if isinstance(path, Index):
	            del (match.context.value[match.path.index])
	        elif isinstance(path, Fields):
	            del (match.context.value[match.path.fields[0]])
        return json_headers

    

    @keyword(name=None, tags=("Settings",))
    def load_headers(self, file_name):
        """*Load Request Headers as JSON file. Returns requestHeaders as JSON Object*

        *Arguments*

            ``file_name``: json file name (with absolute path)

        *Examples*

        | ${requestHeaders}=  |  `Load Headers`  | /path/to/file.json |
        """
        logger.debug("Check if file exists")
        if os.path.isfile(file_name) is False:
            logger.error("JSON file: " + file_name + " not found")
            raise IOError
        elif os.path.getsize(file_name) is 0:
            logger.error("JSON file: " + file_name + " is empty")
            raise IOError
        with open(file_name) as json_file:
            data = json.load(json_file)
        return data

    @keyword(name=None, tags=("Settings",))
    def load_payload(self, file_name):
        """*Load Request Payload as JSON file. Returns requestPayload as JSON Object*

        *Arguments*

            ``file_name``: json file name (with absolute path)

        *Examples*

        | ${requestPayload}=  |  `Load Payload`  | /path/to/file.json |
        """
        logger.debug("Check if file exists")
        if os.path.isfile(file_name) is False:
            logger.error("JSON file: " + file_name + " not found")
            raise IOError
        elif os.path.getsize(file_name) is 0:
            logger.error("JSON file: " + file_name + " is empty")
            raise IOError
        with open(file_name) as json_file:
            data = json.load(json_file)
        return data

    @keyword(name=None, tags=("Settings",))
    def update_header(self, request_headers, header_name, header_value):
        """*Update value of request header by providing header name and header value. Returns updatedHeaders as JSON Object*

        *Arguments*

            ``request_headers``: json object

            ``header_name``: Name of Request Header

            ``header_value``: Value of Request Header

        *Examples*

        | ${updatedHeaders}=  |  `Update Header` | ${requestHeaders} |  X-DNBAPI-UserId  |  TBxxxxx |
        """
        updated_headers = dict(request_headers)
        json_path_expr = parse('$' + '.' + header_name)
        matches = json_path_expr.find(updated_headers)
        if not matches:
            raise AssertionError("Header '%s' " % (header_name) +
                             "did not match anything.")
        for match in matches:
            path = match.path
            if isinstance(path, Index):
                match.context.value[match.path.index] = header_value
            elif isinstance(path, Fields):
                match.context.value[match.path.fields[0]] = header_value

        return updated_headers

    @keyword(name=None, tags=("Settings",))
    def add_headers(self, request_headers, new_headers):
        """*Add a dictionary or list object to existing json header object. Returns updatedHeaders as JSON Object*

    	*Arguments*

        	``request_headers``: json object

        	``new_headers``: dictionary to be added to request_headers

    	*Examples*

    	| ${newHeaders}=     |   Create Dictionary    | latitude=13.1234 	| longitude=130.1234       |
    	| ${updatedHeaders}= |  `Add Headers`         | ${requestHeaders}	| ${newHeaders}            |
    	"""
        updated_headers = dict(request_headers)
        json_path_expr = parse("$")
        for match in json_path_expr.find(updated_headers):
            if type(match.value) is dict:
                match.value.update(new_headers)
            if type(match.value) is list:
                match.value.append(new_headers)
        return updated_headers
        
    @keyword(name=None, tags=("Settings",))
    def add_header(self, request_headers, header_name, header_value):
        """*Add a dictionary or list object to existing json header object. Returns updatedHeaders as JSON Object*

    	*Arguments*

        	``request_headers``: json object

        	``header_name``: name of header to be included
        	
        	``header_value``: value of header to be included

    	*Examples*

    	| ${updatedHeaders}= |  `Add Header`         | ${requestHeaders}	| Authorization | Basic xxxx |
    	"""
        
        new_headers = { header_name : header_value}
        updated_headers = dict(request_headers)
        json_path = parse('$' + '.' + header_name)
        matches = json_path.find(updated_headers)
        if matches:
            raise AssertionError("Header '%s' " % (header_name) +
                             "exists.")
        if not matches:
            json_path_expr = parse("$")
            for match in json_path_expr.find(updated_headers):
                if type(match.value) is dict:
                    match.value.update(new_headers)
                if type(match.value) is list:
                    match.value.append(new_headers)
            return updated_headers
        

    @keyword(name=None, tags=("Settings",))
    def set_path_param(self, endpoint, paramName, paramValue):
        """*Replaces paramName in the given endpoint with paramValue. Returns updatedEndpoint*    

        *Arguments*                                                                      

            ``endpoint``: REST API Service URL with path parameter. For ex: https://testserver/v1/accounts/{accountNumber}/balance

            ``paramName``: Used as a parameterized string. For ex: {accountNumber}                     

            ``paramValue``: Used as a string that is replaced in the paramName provided. 	    	                                                  

        *Examples*                                                                       

        | ${updatedEndpoint} | `Set Path Param` | https://testserver/v1/accounts/{accountNumber}/balance | {accountNumber} | 12085214800 |    
        """
        return endpoint.replace(paramName, paramValue)

    @keyword(name=None, tags=("Settings",))
    def set_query_param(self, endpoint, paramName, paramValue):
        """*Sets the paramName & paramValue in the given endpoint. Returns updatedEndpoint*    

        *Arguments*                                                                      

            ``endpoint``: REST API Service URL. For ex: https://testserver/v1/accounts

            ``paramName``: Used as a Query Parameter string. For ex: accountNumber                     

            ``paramValue``: Used as a string that is added as value of Query Parameter. 	    	                                                  

        *Examples*                                                                       

        | ${updatedEndpoint} | `Set Query Param` | https://testserver/v1/accounts | accountNumber | 12085214800 |    
        """
        if "?" in endpoint:
            updatedEndpoint= endpoint + "&" + paramName + "=" + paramValue
            return updatedEndpoint
        
        if "?" not in endpoint:
            updatedEndpoint=endpoint + "?" + paramName + "=" + paramValue
            return updatedEndpoint

    
    @keyword(name=None, tags=("Assertions",))
    def get_value_from_response(self, response, json_path):
        """*Get Value From Response using JSONPath.  

        Arguments:
            - response: json object. 
            - json_path: jsonpath expression

        Return array of values

        Examples:
        | ${response}=  |  `Get` https://jsonplaceholder.typicode.com/users?_limit=1  |  
        | ${values}=  |  `Get Value From Response`  | ${response} |  $..phone_number |
        """
        json_path_expr = parse(json_path)
        match = json_path_expr.find(response)
        if not match:
            raise AssertionError("No match found with json path '%s' " % (json_path))    
        if match:
            return [match.value for match in json_path_expr.find(response)]
    
    
    ### Internal methods

    def _request(self, endpoint, request, validate=True):
        if not endpoint.startswith(('http://', 'https://')):
            base_url = self.request['scheme'] + "://" + self.request['netloc']
            if not endpoint.startswith('/'):
                endpoint = "/" + endpoint
            endpoint = urljoin(base_url, self.request['path']) + endpoint
        request['url'] = endpoint
        url_parts = urlparse(request['url'])
        request['scheme'] = url_parts.scheme
        request['netloc'] = url_parts.netloc
        request['path'] = url_parts.path
        try:
            response = client(request['method'], request['url'],
                              params=request['query'],
                              json=request['body'],
                              headers=request['headers'],
                              proxies=request['proxies'],
                              cert=request['cert'],
                              timeout=tuple(request['timeout']),
                              allow_redirects=request['allowRedirects'],
                              verify=request['sslVerify'])
        except SSLError as e:
            raise AssertionError("%s to %s SSL certificate verify failed:\n%s" %
                                 (request['method'], request['url'], e))
        except Timeout as e:
            raise AssertionError("%s to %s timed out:\n%s" % (
                request['method'], request['url'], e))
        utc_datetime = datetime.now(tz=utc)
        request['timestamp'] = {
            'utc': utc_datetime.isoformat(),
            'local': utc_datetime.astimezone(get_localzone()).isoformat()
        }
        if validate and self.spec:
            self._assert_spec(self.spec, response)
        instance = self._instantiate(request, response, validate)
        self.instances.append(instance)
        return instance

    def _instantiate(self, request, response, validate_schema=True):
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text
            if response_body:
                logger.warn("Response body content is not JSON. " +
                            "Content-Type is: %s" % response.headers['Content-Type'])
        response = {
            'seconds': response.elapsed.microseconds / 1000 / 1000,
            'status': response.status_code,
            'body': response_body,
            'headers': dict(response.headers)
        }
        schema = deepcopy(self.schema)
        schema['title'] = "%s %s" % (request['method'], request['url'])
        schema['description'] = "%s: %s" % (
            BuiltIn().get_variable_value("${SUITE NAME}"),
            BuiltIn().get_variable_value("${TEST NAME}")
        )
        request_properties = schema['properties']['request']['properties']
        response_properties = schema['properties']['response']['properties']
        if validate_schema:
            if request_properties:
                self._validate_schema(request_properties, request)
            if response_properties:
                self._validate_schema(response_properties, response)
        request_properties['body'] = self._new_schema(request['body'])
        request_properties['query'] = self._new_schema(request['query'])
        response_properties['body'] = self._new_schema(response['body'])
        if 'default' in schema and schema['default']:
            self._add_defaults_to_schema(schema, response)
        return {
            'request': request,
            'response': response,
            'schema': schema,
            'spec': self.spec
        }

    def _assert_spec(self, spec, response):
        request = response.request
        try:
            validate_api_call(spec, raw_request=request, raw_response=response)
        except ValueError as e:
            raise AssertionError(e)

    def _validate_schema(self, schema, json_dict):
        for field in schema:
            self._assert_schema(schema[field], json_dict[field])

    def _assert_schema(self, schema, reality):
        try:
            validate(reality, schema, format_checker=FormatChecker())
        except SchemaError as e:
            raise RuntimeError(e)
        except ValidationError as e:
            raise AssertionError(e)

    def _new_schema(self, value):
        builder = SchemaBuilder(schema_uri=False)
        builder.add_object(value)
        return builder.to_schema()

    def _add_defaults_to_schema(self, schema, response):
        body = response['body']
        schema = schema['properties']['response']['properties']['body']
        if isinstance(body, (dict)) and 'properties' in schema:
            self._add_property_defaults(body, schema['properties'])

    def _add_property_defaults(self, body, schema):
        for key in body:
            if "properties" in schema[key]:
                self._add_property_defaults(body[key], schema[key]['properties'])
            else:
                schema[key]['default'] = body[key]

    def _find_by_field(self, field, response=None, return_schema=True, print_found=True):
        last_instance = self._last_instance_or_error(response)
        schema = None
        paths = []
        if field.startswith("$"):
            value = last_instance['response']['body']
            if return_schema:
                schema = last_instance['schema']['properties']['response']
                schema = schema['properties']['body']
            if field == "$":
                return [{
                    'path': ["response", "body"],
                    'reality': value,
                    'schema': schema
                }]
            try:
                query = parse_jsonpath(field)
            except Exception as e:
                raise RuntimeError("Invalid JSONPath query '%s': %s" % (
                    field, e))
            matches = [str(match.full_path) for match in query.find(value)]
            if not matches:
                raise AssertionError("JSONPath query '%s' " % (field) +
                    "did not match anything.")
            for match in matches:
                path = match.replace("[", "").replace("]", "").split('.')
                paths.append(path)
        else:
            value = last_instance
            if return_schema:
                schema = last_instance['schema']['properties']
            path = field.split()
            paths.append(path)
        return [self._find_by_path(field, path, value, schema, print_found)
                for path in paths]

    def _last_instance_or_error(self, response=None):
        if response:
            return self.input(response)
        else:
            try:
                return self.instances[-1]
            except IndexError:
                raise RuntimeError("No instances: No requests made, " +
                    "and no previous instances loaded in the library import.")

    def _find_by_path(self, field, path, value, schema=None, print_found=True):
        for key in path:
            try:
                value = self._value_by_key(value, key)
            except (KeyError, TypeError):
                if print_found:
                    self.log_json(value,
                        "\n\nProperty '%s' does not exist in:" % (key))
                raise AssertionError(
                    "\nExpected property '%s' was not found." % (field))
            except IndexError:
                if print_found:
                    self.log_json(value,
                        "\n\nIndex '%s' does not exist in:" % (key))
                raise AssertionError(
                    "\nExpected index '%s' did not exist." % (field))
            if schema:
                schema = self._schema_by_key(schema, key, value)
        found = {
            'path': path,
            'reality': value,
            'schema': schema
        }
        return found

    def _value_by_key(self, json, key):
        try:
            return json[int(key)]
        except ValueError:
            return json[key]

    def _schema_by_key(self, schema, key, value):
        if 'properties' in schema:
            schema = schema['properties']
        elif 'items' in schema:
            if isinstance(schema['items'], (dict)):
                schema['items'] = [schema['items']]
            new_schema = self._new_schema(value)
            try:
                return schema['items'][schema['items'].index(new_schema)]
            except ValueError:
                schema['items'].append(new_schema)
                return schema['items'][-1]
        if key not in schema:
            schema[key] = self._new_schema(value)
        return schema[key]

    def _should_add_examples(self):
        return 'examples' in self.schema and isinstance(
            self.schema['examples'], (list))

    def _set_type_validations(self, json_type, schema, validations):
        if validations:
            if "draft-04" in self.schema['$schema']:
                schema_version = "draft-04"
            elif "draft-06" in self.schema['$schema']:
                schema_version = "draft-06"
            else:
                schema_version = "draft-07"
            kws = list(SCHEMA_KEYWORDS['common'][schema_version])
            kws.extend(SCHEMA_KEYWORDS[json_type][schema_version])
        for validation in validations:
            if validation not in kws:
                raise RuntimeError("Unknown JSON Schema (%s)" % (
                    schema_version) + " validation keyword " +
                                   "for %s:\n%s" % (json_type, validation))
            schema[validation] = self.input(validations[validation])
        schema.update({"type": json_type})
