#!/usr/bin/env python

from versions.config import Config
from versions.program import Program
from subprocess import Popen, DEVNULL, PIPE

class Versions(object):
    """Wraps the current environment"""
    
    def __init__(self, outputter):
        """Initializes the environment wrapper

        Args:
            outputter (Outputter): The outputter of the program details.
        """

        self.outputter = outputter
        self.items = []

    def execute_command(self, command):
        
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        rc = p.returncode

        return output, err, p.returncode

    def add_version(self, config):
        """Runs the program to retrieve the program version

        Args:
            args (list): The program name and required args to return the version info.
            formatter (Formatter): The outputter of the program details.
        """

        try:

            output, err, rc = self.execute_command(config.version_command)

            if rc is 0:

                output = output.rstrip().decode("utf-8") 
                output = getattr(self, config.formatter)(config, output)
                self.items.append(output)

            else:
                print(err)
        
        except FileNotFoundError as error:
            program = Program(config.name)
            self.items.append(program)

    def extract(self, config, output):
        """ """

        items = output.split()
        return Program(config.name, items[config.position])

    def extract_go(self, config, output):
        """ """

        items = output.split()
        return Program(config.name, items[2][2:])

    def extract_docker(self, config, output):
        """ """

        items = output.split()
        return Program(config.name, items[2][:-1])

    def output(self):
        """Outputs to based on the provides args"""

        self.outputter.output(self.items)