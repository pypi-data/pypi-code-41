# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.
    Contact: felix@felix-scholz.org
"""
import json
from typing import List, NoReturn


class Acl(object):

    def __init__(self):
        self.__group: List[str] = []
        self.__user: List[str] = []

    def create_from_json(self, acl_json: dict) -> 'Acl':
        """ create from json
        {
            "group": [
                "test_group_1",
                "test_group_2"
            ],
            "user": [
                "everyone"
            ]
        }

        :param dict acl_json:
        :return Acl:
        """
        self.group = acl_json['group']
        self.user = acl_json['user']

        return self

    @property
    def group(self) -> List[str]:
        """Gets the group of this Acl.  # noqa: E501


        :return: The group of this Acl.  # noqa: E501
        :rtype: list[str]
        """
        return self.__group

    @group.setter
    def group(self, group: List[str]) -> NoReturn:
        """Sets the group of this Acl.


        :param group: The group of this Acl.  # noqa: E501
        :type: list[str]
        """

        self.__group = group

    @property
    def user(self) -> List[str]:
        """Gets the user of this Acl.  # noqa: E501


        :return: The user of this Acl.  # noqa: E501
        :rtype: list[str]
        """
        return self.__user

    @user.setter
    def user(self, user: List[str]) -> NoReturn:
        """Sets the user of this Acl.


        :param user: The user of this Acl.  # noqa: E501
        :type: list[str]
        """

        self.__user = user

    def __repr__(self):
        return json.dumps(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Acl):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self) -> dict:
        return {
            'group': self.group,
            'user': self.user
        }
