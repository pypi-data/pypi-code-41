class Entity:
    @classmethod
    def parse(cls, data):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class Account(Entity):
    def __init__(self, short_name: str, author_name: str, author_url: str,
                 access_token: (str, None)=None, auth_url: (str, None)=None,
                 page_count: (int, None)=None):
        self.short_name = short_name
        self.author_name = author_name
        self.author_url = author_url
        self.access_token = access_token
        self.auth_url = auth_url
        self.page_count = page_count

    @classmethod
    def parse(cls, data):
        return cls(short_name=data["short_name"], author_name=data["author_name"],
                   author_url=data["author_url"], access_token=data.get("access_token"),
                   auth_url=data.get("auth_url"), page_count=data.get("page_count"))

    def render(self):
        data = {"short_name": self.short_name, "author_name": self.author_name,
                "author_url": self.author_url}
        if self.access_token is not None:
            data["access_token"] = self.access_token
        if self.auth_url is not None:
            data["auth_url"] = self.auth_url
        if self.page_count is not None:
            data["page_count"] = self.page_count
        return data


class Node(Entity):
    pass


class NodeElement(Node):
    def __init__(self, text: (str, None)=None, tag: (str, None)=None, childrens: (list, None)=None,
                 attrs: (dict, None)=None):
        self.text = text
        self.tag = tag
        self.childrens = childrens
        self.attrs = attrs

    @classmethod
    def parse(cls, data: (str, dict)):
        if isinstance(data, dict):
            tag = data["tag"]
            childrens = data.get("children")
            if childrens is not None:
                childrens = [cls.parse(children) for children in childrens]
            attrs = data.get("attrs")
            return cls(tag=tag, childrens=childrens, attrs=attrs)
        elif isinstance(data, str):
            return cls(text=data)

    def render(self):
        if self.text is None:
            data = {"tag": self.tag}
            if self.childrens is not None:
                data["children"] = self.childrens
            if self.attrs is not None:
                data["attrs"] = self.attrs
            return data
        else:
            return self.text


class Page(Entity):
    def __init__(self, path: str, url: str, title: str, description: str, views: int,
                 author_name: (str, None)=None, author_url: (str, None)=None,
                 image_url: (str, None)=None, content: (list, None)=None,
                 can_edit: (bool, None)=None):
        self.path = path
        self.url = url
        self.title = title
        self.description = description
        self.views = views
        self.author_name = author_name
        self.author_url = author_url
        self.image_url = image_url
        self.content = content
        self.can_edit = can_edit

    @classmethod
    def parse(cls, data):
        path = data["path"]
        url = data["url"]
        title = data["title"]
        description = data["description"]
        views = data["views"]
        author_name = data.get("author_name")
        author_url = data.get("author_url")
        image_url = data.get("image_url")
        content = data.get("content")
        if content is not None:
            content = [NodeElement.parse(c) for c in content]
        can_edit = data.get("can_edit")
        return cls(path=path, url=url, title=title, description=description, views=views,
                   author_name=author_name, author_url=author_url, image_url=image_url,
                   content=content, can_edit=can_edit)

    def render(self):
        data = {"path": self.path, "url": self.url, "title": self.title,
                "description": self.description, "views": self.views}
        if self.author_name is None:
            data["author_name"] = self.author_name
        if self.author_url is None:
            data["author_url"] = self.author_url
        if self.image_url is None:
            data["image_url"] = self.image_url
        if self.content is None:
            data["content"] = [c.render() for c in self.content]
        if self.can_edit is None:
            data["can_edit"] = self.can_edit
        return data
