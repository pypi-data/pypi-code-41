# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.
    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

import json
import pprint
from typing import Optional, NoReturn, Union, List, Tuple
from datetime import datetime

from website_python_client.api.rest_response import RESTResponse
from website_python_client.models.model import Model


class Tag(Model):
    def __init__(self, slug):
        super().__init__()
        self.slug = slug
        
        self.__id: Optional[int] = None
        self.__title: Optional[str] = None
        self.__title_de: Optional[str] = None
        self.__created_at: datetime = datetime.today()
        self.__updated_at: datetime = datetime.today()
        self.__deleted_at: Optional[datetime] = None

    @property
    def id(self) -> Optional[int]:
        """Gets the id of this Tag.

        The tag id.

        :return: The id of this Tag.
        :rtype: int
        """
        return self.__id

    @id.setter
    def id(self, _id: Optional[int]) -> NoReturn:
        """Sets the id of this Tag.

        The tag id.

        :param _id: The id of this Tag.
        :type: int
        """

        self.__id = _id

    @property
    def slug(self) -> str:
        """Gets the slug of this Tag.

        The tag slug.

        :return: The slug of this Tag.
        :rtype: str
        """
        return self.__slug

    @slug.setter
    def slug(self, slug: str) -> NoReturn:
        """Sets the slug of this Tag.

        The tag slug.

        :param slug: The slug of this Tag.
        :type: str
        """
        if slug is None:
            raise ValueError("Invalid value for `slug`, must not be `None`")
        if slug is not None and len(slug) > 128:
            raise ValueError("Invalid value for `slug`, length must be less than or equal to `128`")
        if slug is not None and len(slug) < 1:
            raise ValueError("Invalid value for `slug`, length must be greater than or equal to `1`")

        self.__slug = slug

    @property
    def title(self) -> Optional[str]:
        """Gets the title of this Tag.

        The tag title.

        :return: The title of this Tag.
        :rtype: str
        """
        return self.__title

    @title.setter
    def title(self, title:  Optional[str]) -> NoReturn:
        """Sets the title of this Tag.

        The tag title.

        :param title: The title of this Tag.
        :type: str
        """
        if title is not None and len(title) > 256:
            raise ValueError("Invalid value for `title`, length must be less than or equal to `256`")
        if title is not None and len(title) < 1:
            raise ValueError("Invalid value for `title`, length must be greater than or equal to `1`")

        self.__title = title

    @property
    def title_de(self) -> Optional[str]:
        """Gets the title_de of this Tag.

        The tag german title

        :return: The title_de of this Tag.
        :rtype: str
        """
        return self.__title_de

    @title_de.setter
    def title_de(self, title_de: Optional[str]) -> NoReturn:
        """Sets the title_de of this Tag.

        The tag german title

        :param title_de: The title_de of this Tag.
        :type: str
        """
        if title_de is not None and len(title_de) > 256:
            raise ValueError("Invalid value for `title_de`, length must be less than or equal to `256`")
        if title_de is not None and len(title_de) < 1:
            raise ValueError("Invalid value for `title_de`, length must be greater than or equal to `1`")

        self.__title_de = title_de

    @property
    def created_at(self) -> datetime:
        """Gets the created_at of this Tag.

        The tag create date.

        :return: The created_at of this Tag.
        :rtype: datetime
        """
        return self.__created_at

    @created_at.setter
    def created_at(self, created_at: datetime) -> NoReturn:
        """Sets the created_at of this Tag.

        The tag create date.

        :param created_at: The created_at of this Tag.
        :type: datetime
        """

        self.__created_at = created_at

    @property
    def updated_at(self) -> datetime:
        """Gets the updated_at of this Tag.

        The tag update date.

        :return: The updated_at of this Tag.
        :rtype: datetime
        """
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, updated_at: datetime) -> NoReturn:
        """Sets the updated_at of this Tag.

        The tag update date.

        :param updated_at: The updated_at of this Tag.
        :type: datetime
        """

        self.__updated_at = updated_at

    @property
    def deleted_at(self) -> Optional[datetime]:
        """Gets the deleted_at of this Tag.

        The tag delete date.

        :return: The deleted_at of this Tag.
        :rtype: datetime
        """
        return self.__deleted_at

    @deleted_at.setter
    def deleted_at(self, deleted_at: Optional[datetime]) -> NoReturn:
        """Sets the deleted_at of this Tag.

        The tag delete date.

        :param deleted_at: The deleted_at of this Tag.
        :type: datetime
        """

        self.__deleted_at = deleted_at

    def post_params(self, only: Optional[List[str]] = None) -> List[Tuple[str, str]]:
        params: List[Tuple[str, Union[str, int]]] = []

        if only is None or 'slug' in only:
            params.append(('slug', self.slug))
        if (only is None or 'title' in only) and self.title is not None:
            params.append(('title', self.title))
        if (only is None or 'title_de' in only) and self.title_de is not None:
            params.append(('title_de', self.title_de))

        return params

    def deserialize(self, data: Union[RESTResponse, dict]) -> 'Tag':
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        if isinstance(obj, dict):
            self.id = obj['id']
            self.title = obj['title']
            if 'title_de' in obj:
                self.title_de = obj['title_de']
            if 'created_at' in obj:
                self.created_at = Tag.datetime(obj['created_at'])
            if 'updated_at' in obj:
                self.updated_at = Tag.datetime(obj['updated_at'])
            if 'deleted_at' in obj and obj['deleted_at'] is not None:
                self.deleted_at = Tag.datetime(obj['deleted_at'])

        return self

    @staticmethod
    def deserialize_all(data: RESTResponse) -> List['Tag']:
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        tags = []
        if isinstance(obj, list):
            for tag in obj:
                if 'slug' in tag:
                    tags.append(Tag(tag['slug']).deserialize(tag))

        return tags

    def __repr__(self):
        """For `print` and `pprint`"""
        return pprint.pformat(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Tag):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "title_de": self.title_de,
            "created_at": self.created_at.isoformat(' '),
            "updated_at": self.updated_at.isoformat(' '),
            "deleted_at": self.deleted_at,
        }
