# coding: utf-8

"""
    Cloudsmith API

    The API to the Cloudsmith Service

    OpenAPI spec version: v1
    Contact: support@cloudsmith.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class Namespace(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'name': 'str',
        'slug': 'str',
        'slug_perm': 'str',
        'type_name': 'str'
    }

    attribute_map = {
        'name': 'name',
        'slug': 'slug',
        'slug_perm': 'slug_perm',
        'type_name': 'type_name'
    }

    def __init__(self, name=None, slug=None, slug_perm=None, type_name=None):
        """
        Namespace - a model defined in Swagger
        """

        self._name = None
        self._slug = None
        self._slug_perm = None
        self._type_name = None

        if name is not None:
          self.name = name
        if slug is not None:
          self.slug = slug
        if slug_perm is not None:
          self.slug_perm = slug_perm
        if type_name is not None:
          self.type_name = type_name

    @property
    def name(self):
        """
        Gets the name of this Namespace.
        

        :return: The name of this Namespace.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Namespace.
        

        :param name: The name of this Namespace.
        :type: str
        """

        self._name = name

    @property
    def slug(self):
        """
        Gets the slug of this Namespace.
        

        :return: The slug of this Namespace.
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug):
        """
        Sets the slug of this Namespace.
        

        :param slug: The slug of this Namespace.
        :type: str
        """

        self._slug = slug

    @property
    def slug_perm(self):
        """
        Gets the slug_perm of this Namespace.
        

        :return: The slug_perm of this Namespace.
        :rtype: str
        """
        return self._slug_perm

    @slug_perm.setter
    def slug_perm(self, slug_perm):
        """
        Sets the slug_perm of this Namespace.
        

        :param slug_perm: The slug_perm of this Namespace.
        :type: str
        """

        self._slug_perm = slug_perm

    @property
    def type_name(self):
        """
        Gets the type_name of this Namespace.
        

        :return: The type_name of this Namespace.
        :rtype: str
        """
        return self._type_name

    @type_name.setter
    def type_name(self, type_name):
        """
        Sets the type_name of this Namespace.
        

        :param type_name: The type_name of this Namespace.
        :type: str
        """

        self._type_name = type_name

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, Namespace):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
