# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.


    Contact: felix@felix-scholz.org
    Date: 17. Jul 2019
"""
import json
import os
import pprint

from datetime import datetime
from typing import Optional, NoReturn, Union, Tuple, List

from website_python_client.api.rest_response import RESTResponse
from website_python_client.exceptions import ApiValueError
from website_python_client.models.model import Model


class File(Model):
    """ The File class

    """

    def __init__(self, identifier: str):
        """ Constructor

        :param identifier:
        """
        super().__init__()

        if len(identifier) != 128:
            raise ApiValueError("The file identifier must have 128 sign.")

        self.__id: Optional[int] = None
        self.__identifier: str = identifier
        self.__file_name: Optional[str] = None
        self.__file_size: Optional[int] = None
        self.__content: Optional[str] = None
        self.__content_type: Optional[str] = None
        self.__before: Optional[int] = None
        self.__next: Optional[int] = None
        self.__title: Optional[str] = None
        self.__description: Optional[str] = None
        self.__public: bool = False
        self.__created_at: datetime = datetime.today()
        self.__updated_at: datetime = datetime.today()
        self.__deleted_at: Optional[datetime] = None

    @staticmethod
    def create_from_path(path: str, public: bool = False, title: Optional[str] = None,
                         description: Optional[str] = None) -> 'File':
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                identifier = File.hash_identifier(str(file.read()))
                instance = File(identifier)
                instance.content = path
                instance.title = title
                instance.description = description
                instance.public = public

                return instance

    @property
    def id(self) -> Optional[int]:
        """

        :return int:
        """
        return self.__id

    @id.setter
    def id(self, i: Optional[int]) -> NoReturn:
        """

        :param int i:
        :return None:
        """

        self.__id = i

    @property
    def identifier(self) -> str:
        """

        :return: str
        """
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier: str) -> NoReturn:
        """

        :param str identifier:
        :return:
        """
        if identifier is not None and len(identifier) > 128:
            raise ValueError("Invalid value for `identifier`, length must be less than or equal to `128`")
        if identifier is not None and len(identifier) < 128:
            raise ValueError("Invalid value for `identifier`, length must be greater than or equal to `128`")

        self.__identifier = identifier

    @property
    def file_name(self) -> Optional[str]:
        """Gets the file_name of this File.  # noqa: E501

        The file name.  # noqa: E501

        :return: The file_name of this File.  # noqa: E501
        :rtype: str
        """
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: Optional[str]) -> NoReturn:
        """Sets the file_name of this File.

        The file name.  # noqa: E501

        :param file_name: The file_name of this File.  # noqa: E501
        :type: str
        """

        self.__file_name = file_name

    @property
    def file_size(self) -> Optional[int]:
        """Gets the file_size of this File.  # noqa: E501

        The file size.  # noqa: E501

        :return: The file_size of this File.  # noqa: E501
        :rtype: int
        """
        return self.__file_size

    @file_size.setter
    def file_size(self, file_size: Optional[int]) -> NoReturn:
        """Sets the file_size of this File.

        The file size.  # noqa: E501

        :param file_size: The file_size of this File.  # noqa: E501
        :type: int
        """

        self.__file_size = file_size

    @property
    def content_type(self) -> Optional[str]:
        """Gets the content_type of this File.  # noqa: E501

        The content type of file.  # noqa: E501

        :return: The content_type of this File.  # noqa: E501
        :rtype: str
        """
        return self.__content_type

    @content_type.setter
    def content_type(self, content_type: Optional[str]) -> NoReturn:
        """Sets the content_type of this File.

        The content type of file.  # noqa: E501

        :param content_type: The content_type of this File.  # noqa: E501
        :type: str
        """

        self.__content_type = content_type

    @property
    def content(self) -> Optional[str]:
        """Gets the content_type of this File.

        The content type of file.

        :return: The content of this File.
        :rtype: str
        """
        return self.__content

    @content.setter
    def content(self, content: str) -> NoReturn:
        """Sets the content_type of this File.

        The content type of file.

        :param content: The content_type of this File.
        :type: str
        """

        self.__content = content

    @property
    def before(self) -> Optional[int]:
        """Gets the before of this File.  # noqa: E501

        The file before.  # noqa: E501

        :return: The before of this File.  # noqa: E501
        :rtype: int
        """
        return self.__before

    @before.setter
    def before(self, before: Optional[int]) -> NoReturn:
        """Sets the before of this File.

        The file before.  # noqa: E501

        :param before: The before of this File.  # noqa: E501
        :type: int
        """

        self.__before = before

    @property
    def next(self) -> Optional[int]:
        """Gets the next of this File.  # noqa: E501

        The file after.  # noqa: E501

        :return: The next of this File.  # noqa: E501
        :rtype: int
        """
        return self.__next

    @next.setter
    def next(self, after: Optional[int]):
        """Sets the next of this File.

        The file after.  # noqa: E501

        :param after: The next of this File.  # noqa: E501
        :type: int
        """

        self.__next = after

    @property
    def title(self) -> Optional[str]:
        """Gets the title of this File.  # noqa: E501

        The file title.  # noqa: E501

        :return: The title of this File.  # noqa: E501
        :rtype: str
        """

        return self.__title

    @title.setter
    def title(self, title: Optional[str]) -> NoReturn:
        """Sets the title of this File.

        The file title.  # noqa: E501

        :param title: The title of this File.  # noqa: E501
        :type: str
        """
        if title is not None and 1 > len(title) > 255:
            raise ApiValueError("The File title can have max 255 sign.")

        self.__title = title

    @property
    def description(self) -> Optional[str]:
        """Gets the description of this File.  # noqa: E501

        The file description.  # noqa: E501

        :return: The description of this File.  # noqa: E501
        :rtype: str
        """
        return self.__description

    @description.setter
    def description(self, description: Optional[str]) -> NoReturn:
        """Sets the description of this File.

        The file description.  # noqa: E501

        :param description: The description of this File.  # noqa: E501
        :type: str
        """

        self.__description = description

    @property
    def public(self) -> bool:
        """Gets the public of this File.  # noqa: E501

        Is the file public?  # noqa: E501

        :return: The public of this File.  # noqa: E501
        :rtype: int
        """
        return self.__public

    @public.setter
    def public(self, public: bool) -> NoReturn:
        """Sets the public of this File.

        Is the file public?  # noqa: E501

        :param public: The public of this File.  # noqa: E501
        :type: int
        """

        self.__public = public

    @property
    def created_at(self) -> datetime:
        """Gets the created_at of this File.  # noqa: E501

        The tag create date.  # noqa: E501

        :return: The created_at of this File.  # noqa: E501
        :rtype: datetime
        """
        return self.__created_at

    @created_at.setter
    def created_at(self, created_at: datetime) -> NoReturn:
        """Sets the created_at of this File.

        The tag create date.  # noqa: E501

        :param created_at: The created_at of this File.  # noqa: E501
        :type: datetime
        """

        self.__created_at = created_at

    @property
    def updated_at(self) -> datetime:
        """Gets the updated_at of this File.  # noqa: E501

        The tag update date.  # noqa: E501

        :return: The updated_at of this File.  # noqa: E501
        :rtype: datetime
        """
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, updated_at: datetime) -> NoReturn:
        """Sets the updated_at of this File.

        The tag update date.  # noqa: E501

        :param updated_at: The updated_at of this File.  # noqa: E501
        :type: datetime
        """

        self.__updated_at = updated_at

    @property
    def deleted_at(self) -> Optional[datetime]:
        """Gets the deleted_at of this File.  # noqa: E501

        The tag delete date.  # noqa: E501

        :return: The deleted_at of this File.  # noqa: E501
        :rtype: datetime
        """
        return self.__deleted_at

    @deleted_at.setter
    def deleted_at(self, deleted_at: Optional[datetime]) -> NoReturn:
        """Sets the deleted_at of this File.

        The tag delete date.  # noqa: E501

        :param deleted_at: The deleted_at of this File.  # noqa: E501
        :type: datetime
        """

        self.__deleted_at = deleted_at

    def post_params(self, only: Optional[List[str]] = None) -> List[Tuple[str, str]]:
        params: List[Tuple[str, Union[str, int]]] = []

        if (only is None or 'before' in only) and self.before is not None:
            params.append(('before', self.before))
        if (only is None or 'next' in only) and self.next is not None:
            params.append(('next', self.next))
        if (only is None or 'title' in only) and self.title is not None:
            params.append(('title', self.title))
        if (only is None or 'description' in only) and self.description is not None:
            params.append(('description', self.description))
        if only is None or 'public' in only:
            params.append(('public', int(self.public)))

        return params

    def file_params(self) -> List[Tuple[str, str]]:
        files: List[Tuple[str, str]] = []
        if isinstance(self.content, str):
            if os.path.isfile(self.content):
                files.append(tuple(('content', self.content)))

        return files

    def deserialize(self, data: Union[RESTResponse, dict]) -> 'File':
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        if isinstance(obj, dict):
            self.id = obj['id']
            self.identifier = obj['identifier']
            self.title = obj['title']
            self.file_name = obj['file_name']
            if 'before' in obj:
                if obj['before'] is None or isinstance(obj['before'], int):
                    self.before = obj['before']
                elif isinstance(obj['before'], dict):
                    self.before = File(obj['before']['identifier'])
                    self.before = self.before.deserialize(obj['before'])
            if 'next' in obj:
                if obj['next'] is None or isinstance(obj['next'], int):
                    self.next = obj['next']
                elif isinstance(obj['next'], dict):
                    self.next = File(obj['next']['identifier'])
                    self.next = self.before.deserialize(obj['next'])
            if 'content_type' in obj:
                self.content_type = obj['content_type']
            if 'description' in obj:
                self.description = obj['description']
            if 'file_size' in obj:
                self.file_size = obj['file_size']
            if 'public' in obj:
                self.public = obj['public']
            if 'created_at' in obj:
                self.created_at = File.datetime(obj['created_at'])
            if 'updated_at' in obj:
                self.updated_at = File.datetime(obj['updated_at'])
            if 'deleted_at' in obj and obj['deleted_at'] is not None:
                self.deleted_at = File.datetime(obj['deleted_at'])

        return self

    @staticmethod
    def deserialize_all(data: RESTResponse) -> List['File']:
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        files = []
        if isinstance(obj, list):
            for file in obj:
                if 'identifier' in file:
                    files.append(File(file['identifier']).deserialize(file))

        return files

    def __repr__(self):
        """For `print` and `pprint`"""
        return pprint.pformat(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, File):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "identifier": self.identifier,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "before": self.before,
            "next": self.next,
            "title": self.title,
            "description": self.description,
            "public": self.public,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }
