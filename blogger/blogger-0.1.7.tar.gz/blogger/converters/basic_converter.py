import os
import click
from gtts import gTTS
from .converter import Converter


class BasicConverter(Converter):
    def out(self, text, path, token=None, voice=None, pitch=None, rate=None):
        """
        Convert text to an audio file.

        :param str text: The text that needs to be converted to speech.
        :param str path: The path to the output file.
        """
        if token or voice or pitch or rate:
            raise ValueError(
                "The following options are not supported for the basic converter: {}".format(
                    ", ".join(["token", "voice", "pitch", "rate"])
                )
            )

        if os.path.isfile(path):
            os.remove(path)

        gTTS(text, lang="en").save(path)
