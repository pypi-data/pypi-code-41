import io
import os
from configparser import ConfigParser
from typing import Dict, Any, Callable
from datetime import datetime, timezone


CONFIG_DIR = os.path.expanduser("~/.recept")

# Timestamp format used in configuration
TIMESTAMP_FORMAT = "%Y.%m.%dT%H:%M:%S"


# Converter that convert a value from configuration string
CONVERTERS_FROM_CFG: Dict[Any, Callable[[str], Any]] = {
    bool: lambda value: value.lower() in {"true", "yes", "on"},
    datetime: lambda value: datetime.strptime(
        value, TIMESTAMP_FORMAT
    ).astimezone(timezone.utc),
}


# Converters that convert a value to configuration string
CONVERTERS_TO_CFG: Dict[Any, Callable[[Any], str]] = {
    bool: lambda value: str(bool(value)).lower(),
    datetime: lambda value: value.astimezone(timezone.utc).strftime(
        TIMESTAMP_FORMAT
    ),
}


class Config:
    """Recipes configuration store.

    Args:
        project: Name of the project for which the configuration is loaded and
            saved.
    """

    def __init__(self, project: str):
        self.project = project
        # Load the configuration from ini file
        self._parser = ConfigParser()
        self.load()

    @property
    def config_file(self):
        return os.path.join(CONFIG_DIR, f"{self.project}.ini")

    def __str__(self):
        return f"Config(project={self.project})"

    __repr__ = __str__

    def set(self, section: str, key: str, value: Any, converter: Any = str):
        if section not in self._parser:
            self._parser[section] = {}
        converter = CONVERTERS_TO_CFG.get(converter, converter)
        self._parser[section][key] = converter(value)
        self.save()

    def get(
        self,
        section: str,
        key: str,
        default: Any = None,
        converter: Any = None,
    ):
        value = self._parser.get(section, key, fallback=default)
        if value is default or converter is None:
            return value

        converter = CONVERTERS_FROM_CFG.get(converter, converter)
        return converter(value)

    def load(self):
        if os.path.isfile(self.config_file):
            self._parser.read(self.config_file)

    def save(self):
        # Create configuration directory if it doesn't exist
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with io.open(self.config_file, "w", encoding="utf-8") as f:
            self._parser.write(f)
