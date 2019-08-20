# coding: utf-8

"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 10.0.0-dev.3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


## NOTE: This file is auto generated by the swagger code generator program.
## Do not edit the file manually.

import pprint
import re  # noqa: F401

import six

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.


class ResolverNode(object):

    swagger_types = {
        'container_type': 'str'
    }

    attribute_map = {
        'container_type': 'container_type'
    }

    rattribute_map = {
        'container_type': 'container_type'
    }

    discriminator_value_class_map = {
        'analysis': 'ResolverAnalysisNode',
        'acquisition': 'ResolverAcquisitionNode',
        'file': 'ResolverFileNode',
        'subject': 'ResolverSubjectNode',
        'project': 'ResolverProjectNode',
        'group': 'ResolverGroupNode',
        'gear': 'ResolverGearNode',
        'session': 'ResolverSessionNode'
    }

    def __init__(self, container_type=None):  # noqa: E501
        """ResolverNode - a model defined in Swagger"""
        super(ResolverNode, self).__init__()

        self._container_type = None
        self.discriminator = 'container_type'
        self.alt_discriminator = 'node_type'

        self.container_type = container_type

    @property
    def container_type(self):
        """Gets the container_type of this ResolverNode.


        :return: The container_type of this ResolverNode.
        :rtype: str
        """
        return self._container_type

    @container_type.setter
    def container_type(self, container_type):
        """Sets the container_type of this ResolverNode.


        :param container_type: The container_type of this ResolverNode.  # noqa: E501
        :type: str
        """

        self._container_type = container_type


    @staticmethod
    def positional_to_model(value):
        """Converts a positional argument to a model value"""
        return value

    def return_value(self):
        """Unwraps return value from model"""
        return self

    def get_real_child_model(self, data):
        """Returns the real base class specified by the discriminator"""

        discriminator_value = data.get(self.discriminator)
        if not discriminator_value and self.alt_discriminator:
            discriminator_value = data.get(self.alt_discriminator)
        return self.discriminator_value_class_map.get(discriminator_value.lower())

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ResolverNode):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    # Container emulation
    def __getitem__(self, key):
        """Returns the value of key"""
        key = self._map_key(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Sets the value of key"""
        key = self._map_key(key)
        setattr(self, key, value)

    def __contains__(self, key):
        """Checks if the given value is a key in this object"""
        key = self._map_key(key, raise_on_error=False)
        return key is not None

    def keys(self):
        """Returns the list of json properties in the object"""
        return self.__class__.rattribute_map.keys()

    def values(self):
        """Returns the list of values in the object"""
        for key in self.__class__.attribute_map.keys():
            yield getattr(self, key)

    def items(self):
        """Returns the list of json property to value mapping"""
        for key, prop in self.__class__.rattribute_map.items():
            yield key, getattr(self, prop)

    def get(self, key, default=None):
        """Get the value of the provided json property, or default"""
        key = self._map_key(key, raise_on_error=False)
        if key:
            return getattr(self, key, default)
        return default

    def _map_key(self, key, raise_on_error=True):
        result = self.__class__.rattribute_map.get(key)
        if result is None:
            if raise_on_error:
                raise AttributeError('Invalid attribute name: {}'.format(key))
            return None
        return '_' + result
