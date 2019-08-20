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


class PackagesUploadRaw(object):
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
        'description': 'str',
        'name': 'str',
        'package_file': 'str',
        'republish': 'bool',
        'summary': 'str',
        'version': 'str'
    }

    attribute_map = {
        'description': 'description',
        'name': 'name',
        'package_file': 'package_file',
        'republish': 'republish',
        'summary': 'summary',
        'version': 'version'
    }

    def __init__(self, description=None, name=None, package_file=None, republish=None, summary=None, version=None):
        """
        PackagesUploadRaw - a model defined in Swagger
        """

        self._description = None
        self._name = None
        self._package_file = None
        self._republish = None
        self._summary = None
        self._version = None

        if description is not None:
          self.description = description
        if name is not None:
          self.name = name
        self.package_file = package_file
        if republish is not None:
          self.republish = republish
        if summary is not None:
          self.summary = summary
        if version is not None:
          self.version = version

    @property
    def description(self):
        """
        Gets the description of this PackagesUploadRaw.
        A textual description of this package.

        :return: The description of this PackagesUploadRaw.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this PackagesUploadRaw.
        A textual description of this package.

        :param description: The description of this PackagesUploadRaw.
        :type: str
        """

        self._description = description

    @property
    def name(self):
        """
        Gets the name of this PackagesUploadRaw.
        The name of this package.

        :return: The name of this PackagesUploadRaw.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this PackagesUploadRaw.
        The name of this package.

        :param name: The name of this PackagesUploadRaw.
        :type: str
        """

        self._name = name

    @property
    def package_file(self):
        """
        Gets the package_file of this PackagesUploadRaw.
        The primary file for the package.

        :return: The package_file of this PackagesUploadRaw.
        :rtype: str
        """
        return self._package_file

    @package_file.setter
    def package_file(self, package_file):
        """
        Sets the package_file of this PackagesUploadRaw.
        The primary file for the package.

        :param package_file: The package_file of this PackagesUploadRaw.
        :type: str
        """
        if package_file is None:
            raise ValueError("Invalid value for `package_file`, must not be `None`")

        self._package_file = package_file

    @property
    def republish(self):
        """
        Gets the republish of this PackagesUploadRaw.
        If true, the uploaded package will overwrite any others with the same attributes (e.g. same version); otherwise, it will be flagged as a duplicate.

        :return: The republish of this PackagesUploadRaw.
        :rtype: bool
        """
        return self._republish

    @republish.setter
    def republish(self, republish):
        """
        Sets the republish of this PackagesUploadRaw.
        If true, the uploaded package will overwrite any others with the same attributes (e.g. same version); otherwise, it will be flagged as a duplicate.

        :param republish: The republish of this PackagesUploadRaw.
        :type: bool
        """

        self._republish = republish

    @property
    def summary(self):
        """
        Gets the summary of this PackagesUploadRaw.
        A one-liner synopsis of this package.

        :return: The summary of this PackagesUploadRaw.
        :rtype: str
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """
        Sets the summary of this PackagesUploadRaw.
        A one-liner synopsis of this package.

        :param summary: The summary of this PackagesUploadRaw.
        :type: str
        """

        self._summary = summary

    @property
    def version(self):
        """
        Gets the version of this PackagesUploadRaw.
        The raw version for this package.

        :return: The version of this PackagesUploadRaw.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this PackagesUploadRaw.
        The raw version for this package.

        :param version: The version of this PackagesUploadRaw.
        :type: str
        """

        self._version = version

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
        if not isinstance(other, PackagesUploadRaw):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
