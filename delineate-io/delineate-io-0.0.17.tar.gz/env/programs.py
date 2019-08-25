import threading

from env.values import VersionValue, NotInstalledValue, ErrorValue
from env.config import Config
from env.program import Program
from subprocess import Popen, DEVNULL, PIPE

class Programs(object):
    """Implements the List command for the environment"""
    
    def __init__(self, formatter, outputter):
        """Initializes the environment wrapper

        Args:
            formatter (Formatter): The formatter for program details
            outputter (Outputter): The outputter for program details
        """

        self.formatter = formatter
        self.outputter = outputter
        self.items = []

    def execute_command(self, config, command, formatter = None):
        

        try:
            p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            raw_result, err = p.communicate(b"input data that is passed to subprocess' stdin")
            rc = p.returncode

            trimmed_result = raw_result.rstrip().decode("utf-8") 

            if formatter is None:
                return VersionValue(trimmed_result)
            else:
                return VersionValue(getattr(self, formatter)(config, trimmed_result))
            
        except FileNotFoundError as err:
            return NotInstalledValue()

        except Exception as err:
        
            return ErrorValue()


    def add_version(self, row):
        """Runs the program to retrieve the program version

        Args:
            args (list): The program name and required args to return the version info.
            formatter (Formatter): The outputter of the program details.
        """

        config = Config(row)

        try:
            
            current = self.execute_command(config, config.current_command, config.current_formatter)
            latest = self.execute_command(config, config.latest_command)

            program = Program(config, current, latest)
            self.items.append(program)
            
        except FileNotFoundError as error:
            program = Program(config)
            self.items.append(program)


    def extract(self, config, output):
        """ """

        items = output.split()
        return items[config.position]

    def extract_go(self, config, output):
        """ """

        items = output.split()
        return items[2][2:]

    def extract_docker(self, config, output):
        """ """

        items = output.split()
        return items[2][:-1]


    def output(self):
        """Outputs to based on the provides args"""
        
        # format(self, items, show_commands):
        # def output(self, result):

        result = self.formatter.format(self.items)
        self.outputter.output(result)