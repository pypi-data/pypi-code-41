from abc import ABC, abstractmethod


class Converter(ABC):
    """
    Base class for objects responsible for converting text to audio.
    """

    @abstractmethod
    def out(self, text, path, token=None, voice=None, pitch=None, rate=None):
        """
        Convert text to an audio file.

        :param str text: The text that needs to be converted to speech.
        :param str path: The path to the output file.
        """
