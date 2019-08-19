# -*- coding: utf-8 -*-
"""DNA Center Create HTTP write credentials data model.

Copyright (c) 2019 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import fastjsonschema
import json
from dnacentersdk.exceptions import MalformedRequest

from builtins import *


class JSONSchemaValidator4D9CA8E2431A8A24(object):
    """Create HTTP write credentials request schema definition."""
    def __init__(self):
        super(JSONSchemaValidator4D9CA8E2431A8A24, self).__init__()
        self._validator = fastjsonschema.compile(json.loads(
            '''{
                "items": {
                "properties": {
                "comments": {
                "description":
                 "",
                "type": "string"
                },
                "credentialType": {
                "description":
                 "",
                "enum": [
                "GLOBAL",
                "APP"
                ],
                "type": "string"
                },
                "description":
                 {
                "description":
                 "",
                "type": "string"
                },
                "id": {
                "description":
                 "",
                "type": "string"
                },
                "instanceTenantId": {
                "description":
                 "",
                "type": "string"
                },
                "instanceUuid": {
                "description":
                 "",
                "type": "string"
                },
                "password": {
                "description":
                 "",
                "type": "string"
                },
                "port": {
                "type": "number"
                },
                "secure": {
                "type": "boolean"
                },
                "username": {
                "description":
                 "",
                "type": "string"
                }
                },
                "type": "object"
                },
                "type": "array"
                }'''.replace("\n" + ' ' * 16, '')
        ))

    def validate(self, request):
        try:
            self._validator(request)
        except fastjsonschema.exceptions.JsonSchemaException as e:
            raise MalformedRequest(
                '{} is invalid. Reason: {}'.format(request, e.message)
            )
