import threading
import concurrent.futures

from utils import get_dict_from_csv, get_list_from_csv, execute_command, unexpected_err, print_lines
from dep.config import Config
from dep.dependency import Dependency
from dep.values import Version, NotInstalled, Error
from dep.formatters import TableFormatter, JsonFormatter
from dep.outputters import ConsoleOutputter, FileOutputter

FILENAME = "dep/dependencies.csv"

def install_command(name):
    """Installs one of the dependencies 

    Args:
        name (str): Name of the dependency that can be installed
    """

    try:

        configs = get_dict_from_csv(FILENAME)
        config = Config(configs[name.lower()])

        execute_command(config.install_command)
        msg = "Successfully installed '{}'".format(name)
        print_lines([msg], ['green'])

    except Exception as err:

        unexpected_err(err)


def list_command(out, json):
    """The command for displaying the current environment

    Args:
        out (str): Optional file name to output the 
        json (bool): Indicates if the output should be in json
    """

    try:
        
        formatter, outputter = get_processors(out, json)
        command = Command(formatter, outputter)

        items = get_list_from_csv(FILENAME)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for item in items:
                executor.submit(command.add_dependency, item)

        command.output()

    except Exception as err:
        
        unexpected_err(err)


def get_processors(out, json):
    """Selects the correct processors for formatters and outputters
    
    Args:
        json (bool): Indicates if the output should be in json
    """

    is_file = out is not None
    
    if json:
        formatter = JsonFormatter()
    else:
        in_colour = is_file is False
        formatter = TableFormatter(in_colour)
    
    if is_file:
        outputter = FileOutputter(out)
    else:
        outputter = ConsoleOutputter()

    return formatter, outputter


class Command(object):
    """Implements the List command for the environment"""
    
    def __init__(self, formatter, outputter):
        """Initializes the environment wrapper

        Args:
            formatter (Formatter): The formatter for dependency details
            outputter (Outputter): The outputter for dependency details
        """

        self.formatter = formatter
        self.outputter = outputter
        self.items = []


    def execute(self, config, command, formatter = None):
        
        try:
            result, error, code = execute_command(command)

            if formatter is None:
                return Version(result)
            else:
                return Version(getattr(self, formatter)(config, result))
            
        except FileNotFoundError as err:
            return NotInstalled()

        except Exception as err:
        
            return Error()


    def add_dependency(self, row):
        """Runs the dependency to retrieve the dependency version

        Args:
            args (list): The dependency name and required args to return the version info.
            formatter (Formatter): The formatter of the dependency details.
        """

        config = Config(row)

        try:
            current = self.execute(config, config.current_command, config.current_formatter)
            latest = self.execute(config, config.latest_command)

            dependency = Dependency(config, current, latest)
            self.items.append(dependency)
            
        except FileNotFoundError as error:
            dependency = Dependency(config)
            self.items.append(dependency)


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

        result = self.formatter.format(self.items)
        self.outputter.output(result)