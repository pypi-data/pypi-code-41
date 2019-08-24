
import json

class Config(object):
    """ """

    def __init__(self, row):
        """ """
        
        self.name = row[0]
        self.type = row[1]
        self.version_switch = row[2]

        self.version_command = "{} {}".format(self.name, self.version_switch).split()
        self.newer_command = "{} outdated {}".format(self.type, self.name).split()
        self.update_command = "{} outdated {}".format(self.type, self.name).split()

        if len(row) > 3:
            self.formatter = row[3]
        else:
            self.formatter = "extract"
        
        if len(row) > 4:
            self.position = int(row[4])
        else:
            self.position = 1

    def print(self):

        print(json.dumps(self.__dict__))