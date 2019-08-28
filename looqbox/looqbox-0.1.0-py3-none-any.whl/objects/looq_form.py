import json
from looqbox.objects.looq_object import LooqObject
from collections import OrderedDict


class ObjForm(LooqObject):
    """
    Creates a Looqbox form.

    Attributes:
    --------
        :param dict *fields: Form parameters.
        :param str title: Form title.
        :param str method: Form method ("GET" or "POST").
        :param str action: Form action.
        :param str filepath: Form input file path.

    Example:
    --------
    >>> form = ObjForm({"type": "input", "label": "Loja", "value": "3",
    ...                 "name": "loja", "readonly": TRUE, "style": {"text-align": "center"}},
    ...                {"type": "input", "label": "Produto", "value": "Suco",
    ...                 "name": "plu", "readonly": TRUE, "style": {"text-align": "center"}},
    ...                title="Suco de laranja 350mL")

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """

    def __init__(self, *fields, title=None, method="GET", action=None, filepath=None):
        """
        Creates a view to drag and drop a file that will be read and used in other script of the response.

        Parameters:
        --------
            :param dict *fields: Form parameters.
            :param str title: Form title.
            :param str method: Form method ("GET" or "POST").
            :param str action: Form action.
            :param str filepath: Form input file path.

        Example:
        --------
        >>> form = ObjForm({"type": "input", "label": "Loja", "value": "3",
        ...                 "name": "loja", "readonly": TRUE, "style": {"text-align": "center"}},
        ...                {"type": "input", "label": "Produto", "value": "Suco",
        ...                 "name": "plu", "readonly": TRUE, "style": {"text-align": "center"}},
        ...                title="Suco de laranja 350mL")
        """
        super().__init__()
        if action is None:
            action = ""
        self.title = title
        self.method = method
        self.action = action
        self.filepath = filepath
        self.fields = fields

    @property
    def to_json_structure(self):
        """
        Creates the JSON structure to be read by the FES.

        :return: A JSON string.
        """
        if not isinstance(self.title, list):
            self.title = [self.title]

        json_content = OrderedDict(
            {
                "objectType": "form",
                "title": self.title,
                "method": self.method,
                "action": self.action,
                "filepath": self.filepath,
                "fields": self.fields
            }
        )

        # Transforming in JSON
        form_json = json.dumps(json_content, indent=1)

        return form_json
