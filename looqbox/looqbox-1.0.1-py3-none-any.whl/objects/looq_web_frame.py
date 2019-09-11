from looqbox.objects.looq_object import LooqObject
import json
from collections import OrderedDict


class ObjWebFrame(LooqObject):
    """
    Creates a looqbox web frame from a web content link.
    This functions only works with https links for web security reasons.

    Attributes:
    --------
        :param str src: HTTPS web link of the content.
        :param int width: Width of the frame to be displayed in the interface.
        :param int height: Height of the frame to be displayed in the interface.
        :param bool enable_fullscreen: Enable "fullscreen" button.
        :param bool open_fullscreen: The web frame is opened in fullscreen mode inside the interface.

    Example:
    --------
    >>> frame = ObjWebFrame("https://toggl.com/online-stopwatch/", width=500, height=480)

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """
    def __init__(self, src, width=None, height=500, enable_fullscreen=False, open_fullscreen=False):
        """
        Creates a looqbox web frame from a web content link.
        This functions only works with https links for web security reasons.

        Parameters:
        --------
            :param str src: HTTPS web link of the content.
            :param int width: Width of the frame to be displayed in the interface.
            :param int height: Height of the frame to be displayed in the interface.
            :param bool enable_fullscreen: Enable "fullscreen" button.
            :param bool open_fullscreen: The web frame is opened in fullscreen mode inside the interface.
            :return: A looqbox web frame object to be displayed inside the Looqbox's interface.

        Example:
        --------
        >>> frame = ObjWebFrame("https://toggl.com/online-stopwatch/", width=500, height=480)
        """
        super().__init__()
        self.source = src
        self.width = width
        self.height = height
        self.enable_fullscreen = enable_fullscreen
        self.open_fullscreen = open_fullscreen

    @property
    def to_json_structure(self):
        """
        Creates the JSON structure to be read by the FES.

        :return: A JSON string.
        """
        if self.width is None:
            self.width = ""
        else:
            self.width = str(self.width)

        json_content = OrderedDict(
            {
                "objectType": "webframe",
                "src": self.source,
                "style": {
                    "width": str(self.width),
                    "height": str(self.height)
                },
                "enableFullscreen": self.enable_fullscreen,
                "openFullscreen": self.open_fullscreen,
            }
        )

        # Transforming in JSON
        web_frame_json = json.dumps(json_content, indent=1)

        return web_frame_json
