# Copyright 2017 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy import exceptions


def get_resource_identity(resource):
    if resource is None:
        return None
    else:
        return resource.get('@odata.id', None)


def num_or_none(x):
    """Given a value x it cast as int, float or None

    :param x: The value to transform and return
    :returns: Either None or x cast to an int/float

    """
    if x is None:
        return None

    if isinstance(x, (int, float)):
        return x

    try:
        return int(x)
    except ValueError:
        return float(x)


def get_sub_resource_path_list_by(resource, subresource_name):
    """Helper function to find a list of subresource path

    :param resource: ResourceBase instance on which the name
        gets queried upon.
    :param subresource_name: name of the resource field contains
        a list of dict to fetch the '@odata.id' from.
    """
    if not subresource_name:
        raise ValueError('"subresource_name" cannot be empty')

    if not isinstance(subresource_name, list):
        subresource_name = [subresource_name]

    body = resource.json
    for path_item in subresource_name:
        body = body.get(path_item, {})

    if not body:
        raise exceptions.MissingAttributeError(
            attribute='/'.join(subresource_name), resource=resource.path)

    return [item.get('@data.id') for item in body]


# TODO(linyang): Use the same function in sushy utils after sushy 1.8.1
# is released
def camelcase_to_underscore_joined(camelcase_str):
    """Convert camelCase string to underscore_joined string

    :param camelcase_str: The camelCase string
    :returns: the equivalent underscore_joined string
    """
    if not camelcase_str:
        raise ValueError('"camelcase_str" cannot be empty')

    r = camelcase_str[0].lower()
    for i, letter in enumerate(camelcase_str[1:], 1):
        if letter.isupper():
            try:
                if (camelcase_str[i - 1].islower()
                        or camelcase_str[i + 1].islower()):
                    r += '_'
            except IndexError:
                pass

        r += letter.lower()

    return r
