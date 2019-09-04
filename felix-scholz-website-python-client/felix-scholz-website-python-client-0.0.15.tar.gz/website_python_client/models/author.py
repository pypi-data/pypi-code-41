# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.
    Contact: felix@felix-scholz.org
"""
import json

from datetime import datetime
from typing import Optional, NoReturn

from website_python_client.models import Model


class Author(object):
    def __init__(self):
        self.__date: datetime = datetime.today()
        self.__name: Optional[str] = None
        self.__email: Optional[str] = None

    def create_from_json(self, author_json: dict) -> 'Author':
        """ create author from json
        {
            "name": "Test Tester",
            "email": "test@tester-example.com",
            "date": 1496842299
        }

        :param dict author_json:
        :return Author:
        """
        if isinstance(author_json['date'], int):
            self.date = datetime.fromtimestamp(author_json['date'])
        else:
            self.date = Model.datetime(author_json['date'])
        self.name = author_json['name']
        self.email = author_json['email']

        return self

    @property
    def date(self) -> datetime:
        """Gets the date of this Author.  # noqa: E501

        The author edition date.  # noqa: E501

        :return: The date of this Author.  # noqa: E501
        :rtype: int
        """
        return self.__date

    @date.setter
    def date(self, date: datetime) -> NoReturn:
        """Sets the date of this Author.

        The author edition date.  # noqa: E501

        :param date: The date of this Author.  # noqa: E501
        :type: int
        """

        self.__date = date

    @property
    def name(self) -> Optional[str]:
        """Gets the name of this Author.  # noqa: E501

        The Editor of current change.  # noqa: E501

        :return: The name of this Author.  # noqa: E501
        :rtype: str
        """
        return self.__name

    @name.setter
    def name(self, name: Optional[str]) -> NoReturn:
        """Sets the name of this Author.

        The Editor of current change.  # noqa: E501

        :param name: The name of this Author.  # noqa: E501
        :type: str
        """

        self.__name = name

    @property
    def email(self) -> Optional[str]:
        """Gets the email of this Author.  # noqa: E501

        The email of the editor.  # noqa: E501

        :return: The email of this Author.  # noqa: E501
        :rtype: str
        """
        return self.__email

    @email.setter
    def email(self, email: Optional[str]) -> NoReturn:
        """Sets the email of this Author.

        The email of the editor.  # noqa: E501

        :param email: The email of this Author.  # noqa: E501
        :type: str
        """

        self.__email = email

    def __repr__(self):
        """For `print` and `pprint`"""
        return json.dumps(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Author):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self):
        return {
            'date': int(self.date.timestamp()),
            'email': self.email,
            'name': self.name
        }