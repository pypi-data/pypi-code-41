import json
import datetime
import geopy
import argparse
import yaml


def serialize(obj) -> str:
    """ Serializes an object into json """
    return json.dumps(obj, cls=DateTimeEncoder, sort_keys=True, indent=4)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj) -> str:

        if isinstance(obj, (datetime.date, datetime.datetime)):
            obj = obj.isoformat()
            return obj

        elif isinstance(obj, (geopy.Point)):
            return str([obj.latitude, obj.longitude, obj.altitude])

        else:
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class Settings(object):
    """Simple class to handle library settings"""

    def __init__(self, settings: dict):
        super(Settings, self).__init__()
        for k, v in settings.items():
            self.__dict__[k] = v

    def items(self):
        return self.__dict__.items()

    @classmethod
    def from_args(cls, args, skip_undefined=True):
        settings = dict()

        try:
            if args.settings:
                with open(args.settings, "r") as f:
                    settings = yaml.load(f, Loader=yaml.FullLoader)
        except:
            pass

        for key, value in args.__dict__.items():
            if value is not None or skip_undefined is False:
                if key in settings and settings[key] is None:
                    settings[key] = value
                if key not in settings:
                    settings[key] = value

        return cls(settings)

    def __str__(self):
        return str(self.__dict__)


class ParserHelper(object):
    """
    ParserHelper
    Handles the creation and decoding of arguments
    """

    def __init__(
        self,
        description="timemap arguments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    ):
        super(ParserHelper, self).__init__()
        self._parser = argparse.ArgumentParser(
            description=description, formatter_class=formatter_class
        )
        self._groups = dict()

    @property
    def parser(self):
        """ Returns the parser object """
        return self._parser

    @property
    def arguments(self):
        """ Returns arguments that it can parse and throwing an error otherwise """
        self._arguments, self._unknown_arguments = self.parser.parse_known_args()
        return self._arguments

    @property
    def known_arguments(self):
        """ returns the unknown arguments it could not parse """
        return self._arguments

    @property
    def unkown_arguments(self):
        """ returns the unknown arguments it could not parse """
        return self._unknown_arguments

    def settings(self, settings_class=None, skip_undefined=True) -> "Settings":

        if settings_class is None:
            settings_class = Settings

        settings = settings_class.from_args(self.arguments, skip_undefined)

        return settings

    def __getattr__(self, name):
        if name not in self._groups:
            self._groups[name] = self._parser.add_argument_group(name)

        return self._groups[name]

    def add_file_settings(self):
        """ For file setting handling"""
        self.file_settings.add_argument(
            "--settings",
            type=str,
            required=False,
            default="defaults.yml",
            help="settings file.",
        )

    def dump(self, path):
        """ dumps the arguments into a file """
        with open(path, "w") as f:
            f.write(serialize(vars(self._arguments)))

    @classmethod
    def default_args(cls, text="Time map arguments") -> "ParserHelper":
        parse = cls(description=text)

        parse.add_file_settings()

        return parse

    def __str__(self):
        return serialize(self.__dict__)
