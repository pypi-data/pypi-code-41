
import json

class Config(object):
    """Represents the config for one of the programs"""

    def __init__(self, row):
        """Initializes the config based on a row of data"""
        
        self.name = row[0]
        self.cl_name = row[1]
        self.brew_name = row[2]
        self.type = row[3]
        self.version_switch = row[4]
        self.current_formatter = row[5]
        self.position = int(row[6])

        self.current_command = "{} {}".format(self.name, self.version_switch).split()
        self.latest_command = "{} outdated {}".format(self.type, self.brew_name).split()
        self.update_command = "{} upgrade {}".format(self.type, self.brew_name).split()