from looqbox.objects.looq_object import LooqObject
import json


class ObjHTML(LooqObject):
    """
    Wraps a HTML code in a Looqbox object to be used in the interface.

    Attributes:
    --------
        :param str html: Html code that will be wrapped.

    Example:
    --------
    >>> HTML = ObjHTML("<div> Hello Worlds </div>)

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """
    def __init__(self, html):
        """
        Wraps a HTML code in a Looqbox object to be used in the interface.

        Parameters:
        --------
            :param str html: Html code that will be wrapped.

        Example:
        --------
            HTML = ObjHTML("<div> Hello Worlds </div>)
        """
        super().__init__()
        self.html = html

    @property
    def to_json_structure(self):
        """
        Creates the JSON structure to be read by the FES.

        :return: A JSON string.
        """
        json_content = {"objectType": "html",
                        "html": self.html
                        }

        # Transforming in JSON
        html_json = json.dumps(json_content, indent=1)

        return html_json
