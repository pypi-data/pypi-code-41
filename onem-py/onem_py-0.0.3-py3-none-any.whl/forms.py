import json

from onem import menus
from onem.common import sanitize_method, sanitize_url


class FormItemType(object):
    STRING = 'string'
    INT = 'int'
    FLOAT = 'float'
    DATE = 'date'
    DATETIME = 'datetime'


class FormItem(object):
    def __init__(self, name, item_type, label, header=None, footer=None,
                 url=None, method=None):
        """
        :param name: string used to identify the item
        :param item_type: FormItemType attribute string used to identify the
                          item type
        :param label: string used in the item's description
        :param header: string used to display in header for this form item
                       (overwrites Form.header)
        :param footer: string used to display in header for this form item
                       (overwrites Form.footer)
        :param url: the callback url path triggered after a choice has been set
                    on this form item
        :param method: how the callback url will be triggered
        """
        allowed_item_types = (
            FormItemType.STRING,
            FormItemType.INT,
            FormItemType.DATE,
            FormItemType.DATETIME,
        )
        if item_type not in allowed_item_types:
            raise Exception(f'Invalid type. Allowed: {allowed_item_types}')

        self.name = name
        self.item_type = item_type
        self.label = label

        self.header = header
        self.footer = footer

        if url is not None:
            self.url = sanitize_url(url)
            self.method = sanitize_method(method)
        else:
            self.url = None
            self.method = None

    def as_data(self):
        return {
            'description': self.label,
            'footer': self.footer,
            'header': self.header,
            'method': self.method,
            'name': self.name,
            'path': self.url,
            'type': self.item_type,
        }

    def as_json(self):
        return json.dumps(self.as_data())


class HiddenFormItem(FormItem):
    def __init__(self, name, value):
        super(HiddenFormItem, self).__init__(name, FormItemType.STRING, '')
        self.value = value

    def as_data(self):
        data = super(HiddenFormItem, self).as_data()
        data.update({
            'hidden': True,
            'value': self.value,
        })
        return data


class FormMeta(object):
    """ Meta information for a Form object """
    def __init__(self, status=True, status_in_header=True, confirm=True):
        """
        :param status: boolean whether to show the completion status
        :param status_in_header: boolean whether to show the status in header
                                 or body
        :param confirm: boolean whether the form needs confirmation or not
        """
        self.status = status
        self.status_in_header = status_in_header
        self.confirm = confirm

    def as_data(self):
        return {
            'completion_status_show': self.status,
            'completion_status_in_header': self.status_in_header,
            'confirmation_needed': self.confirm
        }


class Form(object):
    def __init__(self, items, url, header=None, footer=None, method=None,
                 meta=None):
        """
        :param header: string displayed in the header
                       (overwritten by FormItem.header if not None)
        :param footer: string displayed in the footer
                       (overwritten by FormItem.footer if not None)
        :param items: sequence of FormItem instances
        :param url: callback url path triggered after form is finished
        :param method: http method how to callback url will be triggered
        :param meta: FormMeta instance
        """
        self.header = header
        self.footer = footer
        self.items = items

        self.url = sanitize_url(url)
        self.method = sanitize_method(method)

        assert isinstance(items, (list, tuple))
        for item in items:
            assert isinstance(item, (FormItem, FormItemMenu))

        self.meta = meta

        if self.meta is None:
            return

        assert isinstance(self.meta, FormMeta)

    def as_data(self):
        return {
            'type': 'form',
            'header': self.header,
            'footer': self.footer,
            'body': [item.as_data() for item in self.items],
            'meta': self.meta.as_data() if self.meta else None,
            'path': self.url,
            'method': self.method
        }

    def as_json(self):
        return json.dumps(self.as_data())


class FormItemMenuItem(menus.MenuItem):
    def __init__(self, label, value=None, is_option=True, text_search=None):
        super(FormItemMenuItem, self).__init__(
            label, is_option=is_option, text_search=text_search
        )
        if is_option:
            assert value is not None

        self.value = value

    def as_data(self):
        data = super(FormItemMenuItem, self).as_data()
        data['value'] = self.value
        data.pop('path')
        data.pop('method')
        return data


class FormItemMenuMeta(menus.MenuMeta):
    """ Meta information for a FormItemMenu object """
    def __init__(self, auto_select=False, multi_select=False, numbered=False):
        """
        :param auto_select: if true auto selects the option if the menu
            has only one option
        :param multi_select: allow multiple options to be selected
        :param numbered: display numbers instead of letter option markers
        """
        super(FormItemMenuMeta, self).__init__(auto_select=auto_select)

        for k in (multi_select, numbered):
            assert(isinstance(k, bool))

        self.multi_select = multi_select
        self.numbered = numbered

    def as_data(self):
        data = super(FormItemMenuMeta, self).as_data()
        data.update({
            'multi_select': self.multi_select,
            'numbered': self.numbered,
        })
        return data


class FormItemMenu(menus.Menu):
    def __init__(self, name, body, header=None, footer=None, meta=None):
        super(FormItemMenu, self).__init__(
            body, header=header, footer=footer, meta=meta
        )
        self.name = name

    def as_data(self):
        data = super(FormItemMenu, self).as_data()
        data['name'] = self.name
        data['type'] = 'form-menu'
        return data
