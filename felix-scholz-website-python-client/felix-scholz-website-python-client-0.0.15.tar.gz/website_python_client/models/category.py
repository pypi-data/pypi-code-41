# coding: utf-8

"""
    Felix' Website mit Blog

    Contact: felix@felix-scholz.org
"""
from __future__ import absolute_import

import json
import os
import pprint
import re

from datetime import datetime
from typing import NoReturn, Optional, List, Union, Tuple, TYPE_CHECKING

from website_python_client.api.rest_response import RESTResponse
from website_python_client.models.acl import Acl
from website_python_client.models.model import Model
from website_python_client.models.children import Children

from website_python_client.exceptions import ApiValueError

if TYPE_CHECKING:
    from website_python_client.models import Tag, File


class Category(Model):
    def __init__(self, identifier):
        """ Constructor

        :param identifier:
        """
        super().__init__()

        if len(identifier) != 128:
            raise ApiValueError("The category identifier must have 128 sign.")

        self.__id: Optional[int] = None
        self.__identifier: str = identifier
        self.__parent_id: Optional[Union['Category', int]] = None
        self.__title: Optional[str] = None
        self.__before: Optional[Union['Category', int]] = None
        self.__after: Optional[Union['Category', int]] = None
        self.__source: Optional[str] = None
        self.__slug: Optional[str] = None
        self.__description: Optional[str] = None
        self.__children: 'Children' = Children()
        self.__acl: Acl = Acl()
        self.__tags: List[Tag] = []
        self.__preview: List[File] = []
        self.__created_at: datetime = datetime.today()
        self.__updated_at: datetime = datetime.today()
        self.__deleted_at: Optional[datetime] = None

    @staticmethod
    def create_from_json_file(path: List[str], name: str, source: str = 'blog',
                              parent_id: Optional[int] = None) -> 'Category':
        file_path = '/'.join(path + [name]) + '.' + 'kategorie.json'
        if os.path.isfile(file_path):
            with open(file_path) as file:
                post_json: dict = json.load(file)
                post_json['path'] = path
                post_json['source'] = source
                post_json['parent_id'] = parent_id

                return Category(Category.hash_identifier(':::'.join(path + [name]))).create_from_json(post_json)

    def create_from_json(self, category_json: dict) -> 'Category':
        """create a category from json/dict
        {
            "id":"[required] string",
            "name":"[required] string",
            "description":"string",
            "release":612057600,
            "listing":true,
            "parent":"games",
            "children":{
                "categorie":[],
                "post":[]
            },
            "config":{
                "variablen": {}
            },
            "rights": {
                "group": [],
                "user": [
                    "everyone"
                ]
            }
        }
        and a markdown file with equal path and filename

        :param dict category_json:
        :return Category:
        """
        if 'source' in category_json:
            self.source = category_json['source'] + '_' + category_json['id']

        self.slug = category_json['id']
        self.title = category_json['name']
        self.parent_id = category_json['parent_id']
        if 'description' in category_json and category_json['description'] is not '':
            self.description = category_json['description']
        self.acl = Acl().create_from_json(category_json['rights'])
        if 'children' in category_json and isinstance(category_json['children'], dict):
            if 'categorie' in category_json['children'] and isinstance(category_json['children']['categorie'], list):
                for child_category in category_json['children']['categorie']:
                    self.children.categories.append(child_category)
            if 'post' in category_json['children'] and isinstance(category_json['children']['post'], list):
                for child_post in category_json['children']['post']:
                    self.children.posts.append(child_post)

        return self

    @property
    def id(self) -> Optional[int]:
        """Gets the id of this Category.  # noqa: E501

        The Category id  # noqa: E501

        :return: The id of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__id

    @id.setter
    def id(self, _id: Optional[int]) -> NoReturn:
        """Sets the id of this Category.

        The Category id  # noqa: E501

        :param _id: The id of this Category.  # noqa: E501
        :type: int
        """

        self.__id = _id

    @property
    def identifier(self) -> str:
        """Gets the identifier of this Category.  # noqa: E501

        The post identifier, to identifie from source.  # noqa: E501

        :return: The identifier of this Category.  # noqa: E501
        :rtype: str
        """
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier: str) -> NoReturn:
        """Sets the identifier of this Category.

        The post identifier, to identifie from source.  # noqa: E501

        :param identifier: The identifier of this Category.  # noqa: E501
        :type: str
        """
        if len(identifier) != 128:
            raise ApiValueError("The category identifier must have 128 sign.")

        self.__identifier = identifier

    @property
    def parent_id(self) -> Optional[Union['Category', int]]:
        """Gets the parent_id of this Category.  # noqa: E501

        The parent category  # noqa: E501

        :return: The parent_id of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__parent_id

    @parent_id.setter
    def parent_id(self, parent_id: Optional[Union['Category', int]]) -> NoReturn:
        """Sets the parent_id of this Category.

        The parent category  # noqa: E501

        :param parent_id: The parent_id of this Category.  # noqa: E501
        :type: int
        """

        self.__parent_id = parent_id

    @property
    def title(self) -> Optional[str]:
        """Gets the title of this Category.  # noqa: E501

        The category title  # noqa: E501

        :return: The title of this Category.  # noqa: E501
        :rtype: str
        """
        return self.__title

    @title.setter
    def title(self, title: str) -> NoReturn:
        """Sets the title of this Category.

        The category title  # noqa: E501

        :param title: The title of this Category.  # noqa: E501
        :type: str
        """
        if title is None:
            raise ApiValueError("Missing the required parameter `title`")

        self.__title = title

    @property
    def before(self) -> Optional[Union['Category', int]]:
        """Gets the before of this Category.  # noqa: E501

        The category before this  # noqa: E501

        :return: The before of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__before

    @before.setter
    def before(self, before: Optional[Union['Category', int]]) -> NoReturn:
        """Sets the before of this Category.

        The category before this  # noqa: E501

        :param before: The before of this Category.  # noqa: E501
        :type: int
        """

        self.__before = before

    @property
    def after(self) -> Optional[Union['Category', int]]:
        """Gets the after of this Category.  # noqa: E501

        The category after this  # noqa: E501

        :return: The after of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__after

    @after.setter
    def after(self, after: Optional[Union['Category', int]]) -> NoReturn:
        """Sets the after of this Category.

        The category after this  # noqa: E501

        :param after: The after of this Category.  # noqa: E501
        :type: int
        """

        self.__after = after

    @property
    def source(self) -> Optional[str]:
        """Gets the source of this Category.  # noqa: E501

        The category source  # noqa: E501

        :return: The source of this Category.  # noqa: E501
        :rtype: str
        """
        return self.__source

    @source.setter
    def source(self, source: str) -> NoReturn:
        """Sets the source of this Category.

        The category source  # noqa: E501

        :param source: The source of this Category.  # noqa: E501
        :type: str
        """
        if source is not None and len(source) > 1024:
            raise ValueError("Invalid value for `source`, length must be less than or equal to `1024`")  # noqa: E501
        if source is not None and len(source) < 3:
            raise ValueError("Invalid value for `source`, length must be greater than or equal to `3`")  # noqa: E501

        self.__source = source

    @property
    def slug(self) -> Optional[str]:
        """Gets the slug of this Category.  # noqa: E501

        The category slug  # noqa: E501

        :return: The slug of this Category.  # noqa: E501
        :rtype: str
        """
        return self.__slug

    @slug.setter
    def slug(self, slug: str) -> NoReturn:
        """Sets the slug of this Category.

        The category slug  # noqa: E501

        :param slug: The slug of this Category.  # noqa: E501
        :type: str
        """
        if slug is None:
            raise ValueError("Invalid value for `slug`, must not be `None`")
        if slug is not None and not re.search(r'[\w\-:]+', slug):
            raise ValueError(r"Invalid value for `slug`, must be a follow pattern or equal to `/[\w\-\:]+/`")

        self.__slug = slug

    @property
    def description(self) -> Optional[str]:
        """Gets the description of this Category.  # noqa: E501

        The category description  # noqa: E501

        :return: The description of this Category.  # noqa: E501
        :rtype: str
        """
        return self.__description

    @description.setter
    def description(self, description: Optional[str]) -> NoReturn:
        """Sets the description of this Category.

        The category description  # noqa: E501

        :param description: The description of this Category.  # noqa: E501
        :type: str
        """

        self.__description = description

    @property
    def acl(self) -> Acl:
        """Gets the acl of this Category.  # noqa: E501


        :return: The acl of this Category.  # noqa: E501
        :rtype: Acl
        """
        return self.__acl

    @acl.setter
    def acl(self, acl: Acl) -> NoReturn:
        """Sets the acl of this Category.


        :param acl: The acl of this Category.  # noqa: E501
        :type: Acl
        """

        self.__acl = acl

    @property
    def children(self) -> 'Children':
        return self.__children

    @children.setter
    def children(self, children: 'Children') -> NoReturn:
        self.__children = children

    @property
    def tags(self) -> List['Tag']:
        """Gets the tags of this Category.  # noqa: E501

        Add a tag to the category.  # noqa: E501

        :return: The tags of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__tags

    @tags.setter
    def tags(self, tags: List['Tag']) -> NoReturn:
        """Sets the tags of this Category.

        Add a tag to the category.  # noqa: E501

        :param tags: The tags of this Category.  # noqa: E501
        :type: int
        """

        self.__tags = tags

    @property
    def preview(self) -> List['File']:
        """Gets the preview of this Category.  # noqa: E501

        id to a preview images for category  # noqa: E501

        :return: The preview of this Category.  # noqa: E501
        :rtype: int
        """
        return self.__preview

    @preview.setter
    def preview(self, preview: List['File']) -> NoReturn:
        """Sets the preview of this Category.

        id to a preview images for category  # noqa: E501

        :param preview: The preview of this Category.  # noqa: E501
        :type: int
        """

        self.__preview = preview

    @property
    def created_at(self) -> datetime:
        """Gets the created_at of this Category.  # noqa: E501

        The tag create date.  # noqa: E501

        :return: The created_at of this Category.  # noqa: E501
        :rtype: datetime
        """
        return self.__created_at

    @created_at.setter
    def created_at(self, created_at: datetime) -> NoReturn:
        """Sets the created_at of this Category.

        The tag create date.  # noqa: E501

        :param created_at: The created_at of this Category.  # noqa: E501
        :type: datetime
        """

        self.__created_at = created_at

    @property
    def updated_at(self) -> NoReturn:
        """Gets the updated_at of this Category.  # noqa: E501

        The tag update date.  # noqa: E501

        :return: The updated_at of this Category.  # noqa: E501
        :rtype: datetime
        """
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, updated_at: datetime) -> NoReturn:
        """Sets the updated_at of this Category.

        The tag update date.  # noqa: E501

        :param updated_at: The updated_at of this Category.  # noqa: E501
        :type: datetime
        """

        self.__updated_at = updated_at

    @property
    def deleted_at(self) -> datetime:
        """Gets the deleted_at of this Category.  # noqa: E501

        The tag delete date.  # noqa: E501

        :return: The deleted_at of this Category.  # noqa: E501
        :rtype: datetime
        """
        return self.__deleted_at

    @deleted_at.setter
    def deleted_at(self, deleted_at: Optional[datetime]) -> NoReturn:
        """Sets the deleted_at of this Category.

        The tag delete date.  # noqa: E501

        :param deleted_at: The deleted_at of this Category.  # noqa: E501
        :type: datetime
        """

        self.__deleted_at = deleted_at

    def post_params(self, only: Optional[List[str]] = None) -> List[Tuple[str, Union[str, int]]]:
        params: List[Tuple[str, Union[str, int]]] = []

        if only is None or 'identifier' in only:
            params.append(('identifier', self.identifier))
        if (only is None or 'parent_id' in only) and self.parent_id is not None:
            params.append(('parent_id', str(self.parent_id)))
        if only is None or 'title' in only:
            params.append(('title', self.title))
        if (only is None or 'before' in only) and self.before is not None:
            params.append(('before', str(self.before)))
        if (only is None or 'after' in only) and self.after is not None:
            params.append(('after', str(self.after)))
        if (only is None or 'source' in only) and self.source is not None:
            params.append(('source', self.source))
        if only is None or 'slug' in only:
            params.append(('slug', self.slug))
        if (only is None or 'description' in only) and self.description is not None:
            params.append(('description', self.description))
        if (only is None or 'acl' in only) and self.acl is not None:
            params.append(('acl', str(self.acl)))
        if (only is None or 'tags' in only) and len(self.tags) > 0:
            for tag in self.tags:
                params.append(('tags', tag.id))
        if (only is None or 'preview' in only) and len(self.tags) > 0:
            for image in self.preview:
                params.append(('tags', image.id))

        return params

    def deserialize(self, data: Union[RESTResponse, dict]) -> 'Category':
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        if isinstance(obj, dict):
            self.id = obj['id']
            self.title = obj['title']
            self.slug = obj['slug']
            if obj['parent_id'] is None or isinstance(obj['parent_id'], int):
                self.parent_id = obj['parent_id']
            elif isinstance(obj['parent_id'], dict):
                self.parent_id = Category(obj['parent_id']['identifier'])
                self.parent_id = self.parent_id.deserialize(obj['parent_id'])
            if 'acl' in obj:
                self.acl = Acl().create_from_json(obj['acl'])
            if 'after' in obj:
                if obj['after'] is None or isinstance(obj['after'], int):
                    self.after = obj['after']
                elif isinstance(obj['after'], dict):
                    self.after = Category(obj['after']['identifier'])
                    self.after = self.after.deserialize(obj['after'])
            if 'before' in obj:
                if obj['before'] is None or isinstance(obj['before'], int):
                    self.before = obj['before']
                elif isinstance(obj['before'], dict):
                    self.before = Category(obj['before']['identifier'])
                    self.before = self.before.deserialize(obj['before'])
            if 'description' in obj:
                self.description = obj['description']
            if 'source' in obj:
                self.source = obj['source']
            if 'created_at' in obj:
                self.created_at = Category.datetime(obj['created_at'])
            if 'updated_at' in obj:
                self.created_at = Category.datetime(obj['updated_at'])
            if 'deleted_at' in obj and obj['deleted_at'] is not None:
                self.deleted_at = Category.datetime(obj['deleted_at'])
            if 'preview' in obj:
                pass
            if 'tags' in obj:
                pass

        return self

    @staticmethod
    def deserialize_all(data: RESTResponse) -> List['Category']:
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        categories = []
        if isinstance(obj, list):
            for category in obj:
                if 'identifier' in category:
                    categories.append(Category(category['identifier']).deserialize(category))

        return categories

    def __repr__(self):
        """For `print` and `pprint`"""
        return pprint.pformat(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Category):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "identifier": self.identifier,
            "parent_id": self.parent_id,
            "title": self.title,
            "before": self.before,
            "after": self.after,
            "source": self.source,
            "slug": self.slug,
            "description": self.description,
            "acl": self.acl.__dict__(),
            "tags": self.tags,
            "preview": self.preview,
            "created_at": self.created_at.isoformat(' '),
            "updated_at": self.updated_at.isoformat(' '),
            "deleted_at": self.deleted_at
        }
