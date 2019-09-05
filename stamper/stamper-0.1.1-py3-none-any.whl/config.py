
import os
from configparser import SafeConfigParser


class Config(object):
    def __init__(self, path=None):
        self.path = path
        self.default_paths = [
            os.path.expanduser('~/'),
            os.path.join(os.path.dirname(__file__),'../etc')
        ]
        self.config = {}

    @property
    def filename(self):
        return 'stamper.conf'

    @property
    def sections(self):
        return['stamps', 'sum', 'charts', 'collector']

    def look_for_config(self):
        """
        Look for the configuration file, following the path names listed in
        the default paths
        """
        for path in self.default_paths:
            full_path = os.path.join(path, self.filename)
            if os.path.isfile(full_path):
                self.path = full_path
                return full_path
        # if we reach here, self.path will be still None, no valid
        # config files were found, and so we raise an exception
        raise IOError('ERROR - Can not find ' + self.filename + \
                      ' in your environment')

    def load(self):
        if not self.path:
            full_path = self.look_for_config()
        parser = SafeConfigParser()
        parser.read(full_path)
        for section in self.sections:
            self.config[section] = {}
            for name, value in parser.items(section):
                self.config[section][name] = value
        return self.config

    def get(self, section, parameter=None):
        if section not in self.config.keys():
            # perhaps the config hasn't been loaded yet
            self.load()

        if section not in self.sections:
            raise IndexError('ERROR - ' + section + \
                             ' is not one of the available sections: ' + \
                             ', '.join(self.sections))

        if parameter:
            return self.config[section][parameter]

        return self.config[section]
