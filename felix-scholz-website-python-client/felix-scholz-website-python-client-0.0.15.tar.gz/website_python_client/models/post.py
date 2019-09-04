# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.
    Contact: felix@felix-scholz.org
"""
import json
import os
import pprint
from typing import Optional, List, Union, NoReturn, Tuple

from datetime import datetime

from website_python_client.models.tag import Tag

from website_python_client.exceptions import ApiValueError
from website_python_client.models.model import Model
from website_python_client.models.category import Category
from website_python_client.models.acl import Acl
from website_python_client.models.author import Author
from website_python_client.models.file import File
from website_python_client.api.rest_response import RESTResponse


class Post(Model):

    def __init__(self, identifier: str):
        super().__init__()

        if len(identifier) != 128:
            raise ApiValueError("The post identifier must have 128 sign.")

        self.__id: Optional[int] = None
        self.__identifier: str = identifier
        self.__category: Optional[Union[Category, int]] = None
        self.__path: List[str] = []
        self.__source: Optional[str] = None
        self.__slug: Optional[str] = None
        self.__title: str = 'undefined'
        self.__description: Optional[str] = None
        self.__content: Optional[str] = None
        self.__release: datetime = datetime.today()
        self.__listing: bool = False
        self.__author: List[Author] = []
        self.__acl: Acl = Acl()
        self.__created_at: datetime = datetime.today()
        self.__updated_at: datetime = datetime.today()
        self.__deleted_at: Optional[datetime] = None
        self.__tags: List[Union[Tag, str]] = []
        self.__preview: List[Union[File, str]] = []
        self.__images: List[Union[File, str]] = []
        self.__videos: List[File] = []
        self.__src: Optional[Union[File, str]] = None

    @staticmethod
    def create_from_json_file(path: List[str], name: str, source: str = 'blog') -> 'Post':
        file_path = '/'.join(path + [name]) + '.' + 'post.json'
        if os.path.isfile(file_path):
            with open(file_path) as file:
                post_json: dict = json.load(file)
                post_json['path'] = path
                post_json['source'] = source

                return Post(Post.hash_identifier(':::'.join(path + [name]))).create_from_json(post_json)

    def create_from_json(self, post_json: dict) -> 'Post':
        """create a post from json/dict
        {
            "id": "(required) id/filename",
            "name": "post name",
            "description": "post description",
            "release": 1463762100,
            "listing": false,
            "parent": "parent",
            "picture": {
                "preview": [],
                "content": []
            },
            "config": {
                "variablen": [],
                "developer": [
                    {
                        "name": "",
                        "email": "",
                        "date": 0
                    }
                ]
            },
            "rights": {
                "group": [],
                "user": [
                    ""
                ]
            }
        }
        and a markdown file with equal path and filename

        :param dict post_json:
        :return Post:
        """
        if 'source' in post_json:
            self.source = post_json['source'] + '_' + post_json['id']

        self.slug = post_json['id']
        self.title = post_json['name']
        self.path = post_json['path']
        if 'description' in post_json and post_json['description'] is not '':
            self.description = post_json['description']
        self.release = datetime.fromtimestamp(float(post_json['release']))
        if 'public' in post_json:
            if post_json['public'] is None:
                self.listing = True
        if 'listing' in post_json:
            self.listing = post_json['listing']
        self.tags = post_json['path']
        for author in post_json['config']['developer']:
            self.author.append(Author().create_from_json(author))
        self.acl = Acl().create_from_json(post_json['rights'])

        src_path = '/'.join(post_json['path'] + [post_json['id']]) + '.post.md'
        if os.path.isfile(src_path):
            self.src = src_path

        return self

    @property
    def id(self) -> Optional[int]:
        """Gets the id of this Post.

        The post id.

        :return: The id of this Post.
        :rtype: int
        """
        return self.__id

    @id.setter
    def id(self, _id: Optional[int]) -> NoReturn:
        """Sets the id of this Post.

        The post id.

        :param _id: The id of this Post.
        :type: int
        """

        self.__id = _id

    @property
    def identifier(self) -> str:
        """Gets the identifier of this Post.

        The post identifier, to identifie from source.

        :return: The identifier of this Post.
        :rtype: str
        """
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier: str):
        """Sets the identifier of this Post.

        The post identifier, to identifie from source.

        :param identifier: The identifier of this Post.
        :type: str
        """
        if len(identifier) == 128:
            raise ApiValueError("The post identifier must have 128 sign.")

        self.__identifier = identifier

    @property
    def category(self) -> Optional[Union[Category, int]]:
        """Gets the category of this Post.

        The post category.

        :return: The category of this Post.
        :rtype: int
        """
        return self.__category

    @category.setter
    def category(self, category: Optional[Union[Category, int]]):
        """Sets the category of this Post.

        The post category.

        :param category: The category of this Post.
        :type: int
        """

        self.__category = category

    @property
    def path(self) -> List[str]:
        """ get the path

        :return List[str]:
        """
        return self.__path

    @path.setter
    def path(self, path: List[str]) -> NoReturn:
        """ set the path

        :param List[str] path:
        :return:
        """
        self.__path = path

    @property
    def source(self) -> Optional[str]:
        """Gets the source of this Post.

        The quelle of the post.

        :return: The source of this Post.
        :rtype: str
        """
        return self.__source

    @source.setter
    def source(self, source: Optional[str]) -> NoReturn:
        """Sets the source of this Post.

        The source of the post.

        :param source: The source of this Post.
        :type: str
        """

        self.__source = source

    @property
    def slug(self) -> Optional[str]:
        """Gets the slug of this Post.

        A unique slug of post.

        :return: The slug of this Post.
        :rtype: str
        """
        return self.__slug

    @slug.setter
    def slug(self, slug: Optional[str]) -> NoReturn:
        """Sets the slug of this Post.

        A unique slug of post.

        :param slug: The slug of this Post.
        :type: str
        """
        if slug is None:
            raise ValueError("Invalid value for `slug`, must not be `None`")

        self.__slug = slug

    @property
    def title(self) -> Optional[str]:
        """Gets the title of this Post.

        The title of post.

        :return: The title of this Post.
        :rtype: str
        """
        return self.__title

    @title.setter
    def title(self, title: Optional[str]) -> NoReturn:
        """Sets the title of this Post.

        The title of post.

        :param title: The title of this Post.
        :type: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")

        self.__title = title

    @property
    def description(self) -> Optional[str]:
        """Gets the description of this Post.

        A description of post.

        :return: The description of this Post.
        :rtype: str
        """
        return self.__description

    @description.setter
    def description(self, description: Optional[str]) -> NoReturn:
        """Sets the description of this Post.

        A description of post.

        :param description: The description of this Post.
        :type: str
        """

        self.__description = description

    @property
    def content(self) -> Optional[str]:
        """Gets the content of this Post.

        A html content of post.

        :return: The content of this Post.
        :rtype: str
        """
        return self.__content

    @content.setter
    def content(self, content: Optional[str]) -> NoReturn:
        """Sets the content of this Post.

        A html content of post.

        :param content: The content of this Post.
        :type: str
        """

        self.__content = content

    @property
    def release(self) -> datetime:
        """Gets the release of this Post.

        The release date of post.

        :return: The release of this Post.
        :rtype: datetime
        """
        return self.__release

    @release.setter
    def release(self, release: datetime) -> NoReturn:
        """Sets the release of this Post.

        The release date of post.

        :param release: The release of this Post.
        :type: datetime
        """

        self.__release = release

    @property
    def listing(self) -> bool:
        """Gets the listing of this Post.

        The release date of post.

        :return: The listing of this Post.
        :rtype: bool
        """
        return self.__listing

    @listing.setter
    def listing(self, listing: bool) -> NoReturn:
        """Sets the listing of this Post.

        The release date of post.

        :param listing: The listing of this Post.
        :type: bool
        """

        self.__listing = listing

    @property
    def author(self) -> List[Author]:
        """Gets the author of this Post.


        :return: The author of this Post.
        :rtype: List[Author]
        """
        return self.__author

    @author.setter
    def author(self, author: List[Author]):
        """Sets the author of this Post.


        :param author: The author of this Post.
        :type: Author
        """

        self.__author = author

    @property
    def acl(self) -> Acl:
        """Gets the acl of this Post.


        :return: The acl of this Post.
        :rtype: Acl
        """
        return self.__acl

    @acl.setter
    def acl(self, acl: Acl) -> NoReturn:
        """Sets the acl of this Post.


        :param acl: The acl of this Post.
        :type: Acl
        """

        self.__acl = acl

    @property
    def created_at(self) -> datetime:
        """Gets the created_at of this Post.

        The tag create date.

        :return: The created_at of this Post.
        :rtype: datetime
        """
        return self.__created_at

    @created_at.setter
    def created_at(self, created_at: datetime) -> NoReturn:
        """Sets the created_at of this Post.

        The tag create date.

        :param created_at: The created_at of this Post.
        :type: datetime
        """

        self.__created_at = created_at

    @property
    def updated_at(self) -> datetime:
        """Gets the updated_at of this Post.

        The tag update date.

        :return: The updated_at of this Post.
        :rtype: datetime
        """
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, updated_at: datetime) -> NoReturn:
        """Sets the updated_at of this Post.

        The tag update date.

        :param updated_at: The updated_at of this Post.
        :type: datetime
        """

        self.__updated_at = updated_at

    @property
    def deleted_at(self) -> Optional[datetime]:
        """Gets the deleted_at of this Post.

        The tag delete date.

        :return: The deleted_at of this Post.
        :rtype: datetime
        """
        return self.__deleted_at

    @deleted_at.setter
    def deleted_at(self, deleted_at: Optional[datetime]) -> NoReturn:
        """Sets the deleted_at of this Post.

        The tag delete date.

        :param deleted_at: The deleted_at of this Post.
        :type: datetime
        """

        self.__deleted_at = deleted_at

    @property
    def tags(self) -> Union[List[Tag], List[str]]:
        """Gets the tags of this Post.

        the post tags.

        :return: The tags of this Post.
        :rtype: list[Tag]
        """
        return self.__tags

    @tags.setter
    def tags(self, tags: Union[List[Tag], List[str]]) -> NoReturn:
        """Sets the tags of this Post.

        the post tags.

        :param tags: The tags of this Post.
        :type: list[Tag]
        """

        self.__tags = tags

    @property
    def preview(self) -> List[Union[File, str]]:
        """Gets the preview of this Post.

        upload preview images for post

        :return: The preview of this Post.
        :rtype: list[FileIndex]
        """
        return self.__preview

    @preview.setter
    def preview(self, preview: List[Union[File, str]]) -> NoReturn:
        """Sets the preview of this Post.

        upload preview images for post

        :param preview: The preview of this Post.
        :type: list[FileIndex]
        """

        self.__preview = preview

    @property
    def images(self) -> List[Union[File, str]]:
        """Gets the images of this Post.

        upload images for post

        :return: The images of this Post.
        :rtype: list[FileIndex]
        """
        return self.__images

    @images.setter
    def images(self, images: List[Union[File, str]]) -> NoReturn:
        """Sets the images of this Post.

        upload images for post

        :param images: The images of this Post.
        :type: list[FileIndex]
        """

        self.__images = images

    @property
    def videos(self) -> List[File]:
        """Gets the images of this Post.

        upload images for post

        :return: The images of this Post.
        :rtype: list[FileIndex]
        """
        return self.__videos

    @videos.setter
    def videos(self, videos: List[File]) -> NoReturn:
        """Sets the images of this Post.

        upload images for post

        :param videos: The images of this Post.
        :type: list[FileIndex]
        """

        self.__videos = videos

    @property
    def src(self) -> Optional[Union[File, str]]:
        """Gets the src of this Post.


        :return: The src of this Post.
        :rtype: FileIndex
        """
        return self.__src

    @src.setter
    def src(self, src: Optional[Union[File, str]]) -> NoReturn:
        """Sets the src of this Post.


        :param src: The src of this Post.
        :type: FileIndex
        """

        self.__src = src

    def post_params(self, only: Optional[List[str]] = None) -> List[Tuple[str, Union[str, int]]]:
        params: List[Tuple[str, Union[str, int]]] = []
        
        if only is None or 'identifier' in only:
            params.append(('identifier', self.identifier))
        if (only is None or 'source' in only) and self.source is not None:
            params.append(('source', self.source))
        if (only is None or 'slug' in only) and self.slug is not None:
            params.append(('slug', self.slug))
        if only is None or 'title' in only:
            params.append(('title', self.title))
        if (only is None or 'description' in only) and self.description is not None:
            params.append(('description', self.description))
        if (only is None or 'tags' in only) and len(self.tags) > 0:
            for tag in self.tags:
                if isinstance(tag, str):
                    params.append(('tags[]', tag))
        if (only is None or 'path' in only) and len(self.path) > 0:
            for path in self.path:
                if isinstance(path, str):
                    params.append(('path[]', path))
        if (only is None or 'content' in only) and self.content is not None:
            params.append(('content', self.content))
        if (only is None or 'release' in only) and self.release is not None:
            params.append(('release', str(int(self.release.timestamp()))))
        if (only is None or 'listing' in only) and self.listing is not None:
            params.append(('listing', str(int(self.listing))))
        if (only is None or 'authors' in only) and len(self.author) > 0:
            params.append(('authors', str(self.author)))
        if (only is None or 'acl' in only) and self.acl is not None:
            params.append(('acl', str(self.acl)))
        if (only is None or 'preview' in only) and len(self.preview) > 0:
            for file in self.preview:
                if isinstance(file, File) and file.id is not None:
                    params.append(tuple(('preview[]', file.id)))
        if (only is None or 'images' in only) and len(self.images) > 0:
            for file in self.images:
                if isinstance(file, File) and file.id is not None:
                    params.append(tuple(('images[]', file.id)))
        if (only is None or 'src' in only) and isinstance(self.src, File):
            if self.src.id is not None:
                params.append(tuple(('markdown', self.src.id)))

        return params

    @property
    def file_params(self) -> List[Tuple[str, str]]:
        files: List[Tuple[str, str]] = []
        for file in self.preview:
            if isinstance(file, str):
                files.append(tuple(('preview[]', file)))
        for file in self.images:
            if isinstance(file, str):
                files.append(tuple(('images[]', file)))
        if isinstance(self.src, str):
            files.append(tuple(('markdown', self.src)))

        return files

    def deserialize(self, data: Union[RESTResponse, dict]) -> 'Post':
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        if isinstance(obj, dict):
            self.id = obj['id']
            self.title = obj['title']
            self.slug = obj['slug']
            if 'acl' in obj:
                self.acl = Acl().create_from_json(obj['acl'])
            if 'author' in obj:
                self.author = []
                for author in obj['author']:
                    self.author.append(Author().create_from_json(author))
            if 'category' in obj:
                if obj['category'] is None or isinstance(obj['category'], int):
                    self.category = obj['category']
                elif isinstance(obj['category'], dict):
                    self.category = Category(obj['category']['identifier'])
                    self.category = self.category.deserialize(obj['category'])
            if 'description' in obj:
                self.description = obj['description']
            if 'images' in obj:
                self.images = []
                for image in obj['images']:
                    self.images.append(File(image['identifier']).deserialize(image))
            if 'preview' in obj:
                self.preview = []
                for image in obj['preview']:
                    self.preview.append(File(image['identifier']).deserialize(image))
            if 'created_at' in obj:
                self.created_at = Post.datetime(obj['created_at'])
            if 'deleted_at' in obj and obj['deleted_at'] is not None:
                self.deleted_at = Post.datetime(obj['deleted_at'])
            self.updated_at = Post.datetime(obj['updated_at'])
            if 'listing' in obj:
                self.listing = obj['listing']
            if 'release' in obj:
                self.release = self.__class__.datetime(obj['release'])
            if 'source' in obj:
                self.source = obj['source']
            if 'tags' in obj:
                for tag in obj['tags']:
                    self.tags.append(Tag(tag['slug']).deserialize(tag))
            if 'src' in obj and obj['src'] is not None:
                self.src = File(obj['src']['identifier']).deserialize(obj['src'])
            if 'video' in obj:
                for video in obj['video']:
                    self.videos.append(File(video['identifier']).deserialize(video))

        return self

    @staticmethod
    def deserialize_all(data: RESTResponse) -> List['Post']:
        obj = json.loads(data.data) if isinstance(data, RESTResponse) else data
        posts = []
        if isinstance(obj, list):
            for post in obj:
                if 'identifier' in post:
                    posts.append(Post(post['identifier']).deserialize(post))

        return posts

    def __repr__(self):
        """For `print` and `pprint`"""
        return pprint.pformat(self.__dict__())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Post):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __dict__(self):
        return {
            'id': self.id,
            'identifier': self.identifier,
            "category": self.category,
            "path": self.path,
            "source": self.source,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "release": self.release.isoformat(' '),
            "listing": self.listing,
            "author": self.author,
            "acl": self.acl.__dict__(),
            "created_at": self.created_at.isoformat(' '),
            "updated_at": self.updated_at.isoformat(' '),
            "deleted_at": self.deleted_at.isoformat(' ') if self.deleted_at is not None else None,
            "tags": self.tags,
            "preview": self.preview,
            "images": self.images,
            "src": self.src,
            "videos": self.videos,
        }