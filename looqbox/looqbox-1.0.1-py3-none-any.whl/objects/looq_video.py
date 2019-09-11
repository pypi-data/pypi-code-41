import json
import os
import shutil
from looqbox.objects.looq_object import LooqObject
from looqbox.global_calling import GlobalCalling


class ObjVideo(LooqObject):
    """
    Creates a looqbox video object from a video file in the same directory of the script or from a https web link.

    Attributes:
    --------
        :param str src: Source of the audio to be displayed.
        :param bool auto_play: Defines if the video starts as soon as the board is opened.

    Example:
    --------
    >>> video = ObjVideo("videoFile")

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """
    def __init__(self, src, auto_play=False):
        """
        Creates a looqbox video object from a video file in the same directory of the script or from a https web link.

        Parameters:
        --------
            :param str src: Source of the audio to be displayed.
            :param bool auto_play: Defines if the video starts as soon as the board is opened.

        Example:
        --------
        >>> video = ObjVideo("videoFile")
        """
        super().__init__()
        self.source = src
        self.auto_play = auto_play

    @property
    def to_json_structure(self):
        """
        Creates the JSON structure to be read by the FES.

        :return: A JSON string.
        """
        source = self.source
        if 'https://' not in self.source:
            # From global variable looq
            if os.path.dirname(self.source) == GlobalCalling.looq.temp_dir:
                source = "/api/tmp/download/" + os.path.basename(self.source)
            else:
                template_file = os.path.join(GlobalCalling.looq.response_dir() + "/" + self.source)
                temporary_file = GlobalCalling.looq.temp_file(self.source)
                shutil.copy(template_file, temporary_file)
                source = "/api/tmp/download/" + os.path.basename(temporary_file)

        json_content = {"objectType": "video",
                        "src": source,
                        "autoPlay": self.auto_play
                        }

        # Transforming in JSON
        video_json = json.dumps(json_content, indent=1)

        return video_json
