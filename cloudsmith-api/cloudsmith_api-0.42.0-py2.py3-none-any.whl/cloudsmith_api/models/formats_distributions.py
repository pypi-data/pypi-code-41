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


class FormatsDistributions(object):
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
        'self_url': 'str',
        'slug': 'str',
        'variants': 'str'
    }

    attribute_map = {
        'name': 'name',
        'self_url': 'self_url',
        'slug': 'slug',
        'variants': 'variants'
    }

    def __init__(self, name=None, self_url=None, slug=None, variants=None):
        """
        FormatsDistributions - a model defined in Swagger
        """

        self._name = None
        self._self_url = None
        self._slug = None
        self._variants = None

        if name is not None:
          self.name = name
        if self_url is not None:
          self.self_url = self_url
        if slug is not None:
          self.slug = slug
        if variants is not None:
          self.variants = variants

    @property
    def name(self):
        """
        Gets the name of this FormatsDistributions.
        

        :return: The name of this FormatsDistributions.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this FormatsDistributions.
        

        :param name: The name of this FormatsDistributions.
        :type: str
        """

        self._name = name

    @property
    def self_url(self):
        """
        Gets the self_url of this FormatsDistributions.
        

        :return: The self_url of this FormatsDistributions.
        :rtype: str
        """
        return self._self_url

    @self_url.setter
    def self_url(self, self_url):
        """
        Sets the self_url of this FormatsDistributions.
        

        :param self_url: The self_url of this FormatsDistributions.
        :type: str
        """

        self._self_url = self_url

    @property
    def slug(self):
        """
        Gets the slug of this FormatsDistributions.
        The slug identifier for this distribution

        :return: The slug of this FormatsDistributions.
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug):
        """
        Sets the slug of this FormatsDistributions.
        The slug identifier for this distribution

        :param slug: The slug of this FormatsDistributions.
        :type: str
        """

        self._slug = slug

    @property
    def variants(self):
        """
        Gets the variants of this FormatsDistributions.
        

        :return: The variants of this FormatsDistributions.
        :rtype: str
        """
        return self._variants

    @variants.setter
    def variants(self, variants):
        """
        Sets the variants of this FormatsDistributions.
        

        :param variants: The variants of this FormatsDistributions.
        :type: str
        """

        self._variants = variants

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
        if not isinstance(other, FormatsDistributions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
