import base64
import requests
from blogger.commands.voices import VOICES
from .converter import Converter


class GTTSConverter(Converter):
    def __init__(self):
        super().__init__()
        self.default_pitch = -1.0
        self.default_rate = 0.8
        self.voice_options = map(lambda voice: voice[0], VOICES)

    def out(self, text, path, token=None, voice=None, pitch=None, rate=None):
        """
        Convert text to an audio file.

        :param str text: The text that needs to be converted to speech.
        :param str path: The path to the output file.
        """
        voice = voice or "US-D"
        pitch = min(max(pitch or self.default_pitch, -20), 20)
        rate = min(max(rate or self.default_rate, 0.0), 4.0)

        if voice not in self.voice_options:
            raise ValueError("The voice {} is not supported. Please see `blogger voices -l` for options.".format(voice))

        try:
            res = requests.post(
                "https://texttospeech.googleapis.com/v1/text:synthesize?key={}".format(token),
                json={
                    "input": {"text": text},
                    "voice": {"languageCode": "en-{}".format(voice[0:2]).lower(), "name": self._voice_key(voice)},
                    "audioConfig": {"audioEncoding": "LINEAR16", "pitch": pitch, "speakingRate": rate},
                },
                headers=self._headers,
            )
        except Exception as e:
            raise ValueError("There was a problem making a request to the google text to speech API: {}".format(e))

        if not res.ok:
            raise ValueError("The google text to speech API returned a bad status code [{}]. Make sure you have provided a valid token.".format(res.status_code))

        try:
            with open(path, "wb") as file:
                file.write(bytearray(base64.b64decode(res.json()["audioContent"])))
        except Exception as e:
            raise ValueError("Cannot successfully write to the path {}: {}".format(path, e))

    def _voice_key(self, user_key):
        for voice in VOICES:
            if voice[0] == user_key:
                return voice[2]
        raise ValueError("The voice {} is not supported. Please see `blogger voices -l` for options.".format(voice))

    @property
    def _headers(self):
        return {"Content-Type": "application/json; charset=utf-8"}
