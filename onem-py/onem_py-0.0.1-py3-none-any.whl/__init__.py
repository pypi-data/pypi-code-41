import json

from . import menus, forms


class Response(object):
    def __init__(self, obj):
        """
        :param obj: a Menu of Form instance
        """
        assert isinstance(obj, (menus.Menu, forms.Form))

        self.object = obj

    def as_data(self):
        return {
            'content_type': self.object.as_data()['type'],
            'content': self.object.as_data()
        }

    def as_json(self):
        return json.dumps(self.as_data())
