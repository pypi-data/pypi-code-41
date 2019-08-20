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


class PackagesUploadMaven(object):
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
        'artifact_id': 'str',
        'group_id': 'str',
        'javadoc_file': 'str',
        'package_file': 'str',
        'packaging': 'str',
        'pom_file': 'str',
        'republish': 'bool',
        'sources_file': 'str',
        'version': 'str'
    }

    attribute_map = {
        'artifact_id': 'artifact_id',
        'group_id': 'group_id',
        'javadoc_file': 'javadoc_file',
        'package_file': 'package_file',
        'packaging': 'packaging',
        'pom_file': 'pom_file',
        'republish': 'republish',
        'sources_file': 'sources_file',
        'version': 'version'
    }

    def __init__(self, artifact_id=None, group_id=None, javadoc_file=None, package_file=None, packaging=None, pom_file=None, republish=None, sources_file=None, version=None):
        """
        PackagesUploadMaven - a model defined in Swagger
        """

        self._artifact_id = None
        self._group_id = None
        self._javadoc_file = None
        self._package_file = None
        self._packaging = None
        self._pom_file = None
        self._republish = None
        self._sources_file = None
        self._version = None

        if artifact_id is not None:
          self.artifact_id = artifact_id
        if group_id is not None:
          self.group_id = group_id
        if javadoc_file is not None:
          self.javadoc_file = javadoc_file
        self.package_file = package_file
        if packaging is not None:
          self.packaging = packaging
        if pom_file is not None:
          self.pom_file = pom_file
        if republish is not None:
          self.republish = republish
        if sources_file is not None:
          self.sources_file = sources_file
        if version is not None:
          self.version = version

    @property
    def artifact_id(self):
        """
        Gets the artifact_id of this PackagesUploadMaven.
        The ID of the artifact.

        :return: The artifact_id of this PackagesUploadMaven.
        :rtype: str
        """
        return self._artifact_id

    @artifact_id.setter
    def artifact_id(self, artifact_id):
        """
        Sets the artifact_id of this PackagesUploadMaven.
        The ID of the artifact.

        :param artifact_id: The artifact_id of this PackagesUploadMaven.
        :type: str
        """

        self._artifact_id = artifact_id

    @property
    def group_id(self):
        """
        Gets the group_id of this PackagesUploadMaven.
        Artifact's group ID.

        :return: The group_id of this PackagesUploadMaven.
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """
        Sets the group_id of this PackagesUploadMaven.
        Artifact's group ID.

        :param group_id: The group_id of this PackagesUploadMaven.
        :type: str
        """

        self._group_id = group_id

    @property
    def javadoc_file(self):
        """
        Gets the javadoc_file of this PackagesUploadMaven.
        Adds bundled Java documentation to the Maven package

        :return: The javadoc_file of this PackagesUploadMaven.
        :rtype: str
        """
        return self._javadoc_file

    @javadoc_file.setter
    def javadoc_file(self, javadoc_file):
        """
        Sets the javadoc_file of this PackagesUploadMaven.
        Adds bundled Java documentation to the Maven package

        :param javadoc_file: The javadoc_file of this PackagesUploadMaven.
        :type: str
        """

        self._javadoc_file = javadoc_file

    @property
    def package_file(self):
        """
        Gets the package_file of this PackagesUploadMaven.
        The primary file for the package.

        :return: The package_file of this PackagesUploadMaven.
        :rtype: str
        """
        return self._package_file

    @package_file.setter
    def package_file(self, package_file):
        """
        Sets the package_file of this PackagesUploadMaven.
        The primary file for the package.

        :param package_file: The package_file of this PackagesUploadMaven.
        :type: str
        """
        if package_file is None:
            raise ValueError("Invalid value for `package_file`, must not be `None`")

        self._package_file = package_file

    @property
    def packaging(self):
        """
        Gets the packaging of this PackagesUploadMaven.
        Artifact's Maven packaging type.

        :return: The packaging of this PackagesUploadMaven.
        :rtype: str
        """
        return self._packaging

    @packaging.setter
    def packaging(self, packaging):
        """
        Sets the packaging of this PackagesUploadMaven.
        Artifact's Maven packaging type.

        :param packaging: The packaging of this PackagesUploadMaven.
        :type: str
        """

        self._packaging = packaging

    @property
    def pom_file(self):
        """
        Gets the pom_file of this PackagesUploadMaven.
        The POM file is an XML file containing the Maven coordinates.

        :return: The pom_file of this PackagesUploadMaven.
        :rtype: str
        """
        return self._pom_file

    @pom_file.setter
    def pom_file(self, pom_file):
        """
        Sets the pom_file of this PackagesUploadMaven.
        The POM file is an XML file containing the Maven coordinates.

        :param pom_file: The pom_file of this PackagesUploadMaven.
        :type: str
        """

        self._pom_file = pom_file

    @property
    def republish(self):
        """
        Gets the republish of this PackagesUploadMaven.
        If true, the uploaded package will overwrite any others with the same attributes (e.g. same version); otherwise, it will be flagged as a duplicate.

        :return: The republish of this PackagesUploadMaven.
        :rtype: bool
        """
        return self._republish

    @republish.setter
    def republish(self, republish):
        """
        Sets the republish of this PackagesUploadMaven.
        If true, the uploaded package will overwrite any others with the same attributes (e.g. same version); otherwise, it will be flagged as a duplicate.

        :param republish: The republish of this PackagesUploadMaven.
        :type: bool
        """

        self._republish = republish

    @property
    def sources_file(self):
        """
        Gets the sources_file of this PackagesUploadMaven.
        Adds bundled Java source code to the Maven package.

        :return: The sources_file of this PackagesUploadMaven.
        :rtype: str
        """
        return self._sources_file

    @sources_file.setter
    def sources_file(self, sources_file):
        """
        Sets the sources_file of this PackagesUploadMaven.
        Adds bundled Java source code to the Maven package.

        :param sources_file: The sources_file of this PackagesUploadMaven.
        :type: str
        """

        self._sources_file = sources_file

    @property
    def version(self):
        """
        Gets the version of this PackagesUploadMaven.
        The raw version for this package.

        :return: The version of this PackagesUploadMaven.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this PackagesUploadMaven.
        The raw version for this package.

        :param version: The version of this PackagesUploadMaven.
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
        if not isinstance(other, PackagesUploadMaven):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
