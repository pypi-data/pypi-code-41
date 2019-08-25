import click
import os
import csv
import concurrent.futures
from termcolor import colored, cprint
from env.config import Config
from env.programs import Programs
from env.formatters import TableFormatter, JsonFormatter
from env.outputters import ConsoleOutputter, FileOutputter

@click.group()
def environment():
    """Defines the group for environment commands"""
    pass


@environment.command()
@click.option('--out', '-o', help='The output file for the results')
@click.option('--json', '-j', is_flag=True, default=False)
def list(out, json):
    """The command for displaying the current environment

    Args:
        out (str): Optional file name to output the 
        json (bool): Indicates if the output should be in json
    """

    try:
        
        formatter, outputter = get_processors(out, json)
        command = Programs(formatter, outputter)

        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "programs.csv")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter = ',')
                
                for row in csv_reader:
                    executor.submit(command.add_version, row)

        command.output()

    except Exception as error:
        
        print()
        print("Unexpected error:")
        print(colored(error, 'red'))
        print()


def get_processors(out, json):

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