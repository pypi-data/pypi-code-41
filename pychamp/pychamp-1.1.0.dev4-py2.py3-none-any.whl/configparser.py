"""
Date : 2019-09-05
Author: Sagar Paudel
Description : This is a utility module which can be used for configuration
            parsing and database connection.
"""

import configparser
import json
import os


class ConfigParser(object):
    """
    This class can be used for parsing `ini` and `json` configuration file.
    """

    def __init__(self, type="ini"):
        self.type = type

    def read(self, FILE_PATH):
        """
        It reads the configuration file.
        """
        try:
            if os.path.isfile(FILE_PATH):
                if self.type == "ini":
                    self.CONFIG = configparser.ConfigParser()
                    self.CONFIG.read(FILE_PATH)

                elif self.type == "json":
                    with open(FILE_PATH, "r") as read_file:
                        self.CONFIG = json.load(read_file)
            else:
                raise Exception("{} not exist!!".format(FILE_PATH))
        except Exception as e:
            raise Exception(e)

    def get(self, *args):
        """
        It returns the value of given key.
        """
        VAL = self.CONFIG
        for arg in args:
            VAL = VAL[arg]
        return VAL
