import json

from onem.common import sanitize_method, sanitize_url


class MenuItem(object):
    def __init__(self, label, url=None, method=None, is_option=True,
                 text_search=None):
        """
        :param label: string used in the item's description
        :param url: the callback url path triggered when accessing this item
        :param method: how the callback url will be triggered
        :param is_option: bool to indicate whether the item is an option item
            or a separator item. The separator option body are
            used for presentational purposes only, so url and
            method won't count here
        :param text_search: if present this text will be used as search base
            against user input to narrow down the displayed options
        """
        self.is_option = is_option

        if not self.is_option:
            self.label = label
            self.url = None
            self.method = None
            self.text_search = None
            return

        self.label = label
        self.url = sanitize_url(url)
        self.method = sanitize_method(method)
        self.text_search = text_search

    def as_data(self):
        return {
            'description': self.label,
            'method': self.method,
            'path': self.url,
            'type': 'option' if self.is_option else 'content',
            'text_search': self.text_search
        }

    def as_json(self):
        return json.dumps(self.as_data())


class MenuMeta(object):
    """ Meta information for a Menu object """
    def __init__(self, auto_select=True):
        """
        :param auto_select: if there is one option in the menu, this parameter
                            indicates whether an auto selection will happen
        """
        assert(isinstance(auto_select, bool))
        self.auto_select = auto_select

    def as_data(self):
        return {
            'auto_select': self.auto_select,
        }


class Menu(object):
    def __init__(self, body, header=None, footer=None, meta=None):
        """
        :param body: sequence of MenuItem instances
        :param header: string displayed in the header
        :param footer: string displayed in the footer
        :param meta: MenuMeta instance
        """
        self.header = header
        self.footer = footer

        assert isinstance(body, (list, tuple))
        for item in body:
            assert isinstance(item, MenuItem)

        self.body = body

        self.meta = meta
        if self.meta is None:
            return

        assert isinstance(self.meta, MenuMeta)

    def as_data(self):
        return {
            'type': 'menu',
            'header': self.header,
            'footer': self.footer,
            'body': [item.as_data() for item in self.body],
            'meta': self.meta.as_data() if self.meta else None,
        }

    def as_json(self):
        return json.dumps(self.as_data())
