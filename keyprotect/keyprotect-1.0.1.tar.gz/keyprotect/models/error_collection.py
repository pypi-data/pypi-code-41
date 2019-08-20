# coding: utf-8

"""
    IBM Key Protect API

    IBM Key Protect helps you provision encrypted keys for apps across IBM Cloud. As you manage the lifecycle of your keys, you can benefit from knowing that your keys are secured by cloud-based FIPS 140-2 Level 2 hardware security modules (HSMs) that protect against theft of information. You can use the Key Protect API to store, generate, and retrieve your key material. Keys within the service can protect any type of data in your symmetric key based encryption solution.  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class ErrorCollection(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'collection_type': 'str',
        'collection_total': 'int',
        'resources': 'list[Error]'
    }

    attribute_map = {
        'collection_type': 'collectionType',
        'collection_total': 'collectionTotal',
        'resources': 'resources'
    }

    def __init__(self, collection_type='application/vnd.ibm.kms.error+json', collection_total=None, resources=None):  # noqa: E501
        """ErrorCollection - a model defined in OpenAPI"""  # noqa: E501

        self._collection_type = None
        self._collection_total = None
        self._resources = None
        self.discriminator = None

        if collection_type is not None:
            self.collection_type = collection_type
        if collection_total is not None:
            self.collection_total = collection_total
        self.resources = resources

    @property
    def collection_type(self):
        """Gets the collection_type of this ErrorCollection.  # noqa: E501

        The type of resources in the resource array.  # noqa: E501

        :return: The collection_type of this ErrorCollection.  # noqa: E501
        :rtype: str
        """
        return self._collection_type

    @collection_type.setter
    def collection_type(self, collection_type):
        """Sets the collection_type of this ErrorCollection.

        The type of resources in the resource array.  # noqa: E501

        :param collection_type: The collection_type of this ErrorCollection.  # noqa: E501
        :type: str
        """

        self._collection_type = collection_type

    @property
    def collection_total(self):
        """Gets the collection_total of this ErrorCollection.  # noqa: E501

        The number of elements in the resource array.  # noqa: E501

        :return: The collection_total of this ErrorCollection.  # noqa: E501
        :rtype: int
        """
        return self._collection_total

    @collection_total.setter
    def collection_total(self, collection_total):
        """Sets the collection_total of this ErrorCollection.

        The number of elements in the resource array.  # noqa: E501

        :param collection_total: The collection_total of this ErrorCollection.  # noqa: E501
        :type: int
        """

        self._collection_total = collection_total

    @property
    def resources(self):
        """Gets the resources of this ErrorCollection.  # noqa: E501


        :return: The resources of this ErrorCollection.  # noqa: E501
        :rtype: list[Error]
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """Sets the resources of this ErrorCollection.


        :param resources: The resources of this ErrorCollection.  # noqa: E501
        :type: list[Error]
        """
        if resources is None:
            raise ValueError("Invalid value for `resources`, must not be `None`")  # noqa: E501

        self._resources = resources

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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
        if not isinstance(other, ErrorCollection):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
