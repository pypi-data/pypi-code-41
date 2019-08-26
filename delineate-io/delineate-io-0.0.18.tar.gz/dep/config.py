
import json

class Config(dict):
    """Represents the config for one of the programs"""

    def __init__(self, data):
        """Initializes the config based on a row of data
        
        Args:
            data (array): An data of the data that provides inputs
        """
        
        super().__init__()
        self.__dict__ = self
        
        self.name = data[0]
        self.cl_name = data[1]
        self.brew_name = data[2]
        self.type = data[3]
        self.version_switch = data[4]
        self.current_formatter = data[5]
        self.position = int(data[6])

        self.current_command = "{} {}".format(self.cl_name, self.version_switch).split()
        self.install_command = "{} install {}".format(self.type, self.brew_name).split()
        self.latest_command = "{} outdated {}".format(self.type, self.brew_name).split()
        self.update_command = "{} upgrade {}".format(self.type, self.brew_name).split()