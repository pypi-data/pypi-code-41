# -*- coding: utf-8 -*-
"""DNA Center Claim Device data model.

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


class JSONSchemaValidatorD8A619974A8A8C48(object):
    """Claim Device request schema definition."""
    def __init__(self):
        super(JSONSchemaValidatorD8A619974A8A8C48, self).__init__()
        self._validator = fastjsonschema.compile(json.loads(
            '''{
                "properties": {
                "configFileUrl": {
                "description":
                 "",
                "type": "string"
                },
                "configId": {
                "description":
                 "",
                "type": "string"
                },
                "deviceClaimList": {
                "description":
                 "",
                "items": {
                "properties": {
                "configList": {
                "description":
                 "",
                "items": {
                "properties": {
                "configId": {
                "description":
                 "",
                "type": "string"
                },
                "configParameters": {
                "description":
                 "",
                "items": {
                "properties": {
                "key": {
                "description":
                 "",
                "type": "string"
                },
                "value": {
                "description":
                 "",
                "type": "string"
                }
                },
                "type": "object"
                },
                "type": "array"
                }
                },
                "type": "object"
                },
                "type": "array"
                },
                "deviceId": {
                "description":
                 "",
                "type": "string"
                },
                "licenseLevel": {
                "description":
                 "",
                "type": "string"
                },
                "licenseType": {
                "description":
                 "",
                "type": "string"
                },
                "topOfStackSerialNumber": {
                "description":
                 "",
                "type": "string"
                }
                },
                "type": "object"
                },
                "type": "array"
                },
                "fileServiceId": {
                "description":
                 "",
                "type": "string"
                },
                "imageId": {
                "description":
                 "",
                "type": "string"
                },
                "imageUrl": {
                "description":
                 "",
                "type": "string"
                },
                "populateInventory": {
                "type": "boolean"
                },
                "projectId": {
                "description":
                 "",
                "type": "string"
                },
                "workflowId": {
                "description":
                 "",
                "type": "string"
                }
                },
                "type": "object"
                }'''.replace("\n" + ' ' * 16, '')
        ))

    def validate(self, request):
        try:
            self._validator(request)
        except fastjsonschema.exceptions.JsonSchemaException as e:
            raise MalformedRequest(
                '{} is invalid. Reason: {}'.format(request, e.message)
            )
