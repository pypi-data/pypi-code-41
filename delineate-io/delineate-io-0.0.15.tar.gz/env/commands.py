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
@click.option('--show-commands', '-sc', is_flag=True, default=False)
def list(out, show_commands):
    """The command for displaying the current environment

    Args:
        out (str): Optional file name to output the 
        show_commands (boolean): Indicates in the commands should be shown in the output
    """
    
    command = Programs(TableFormatter(), ConsoleOutputter())

    path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(path, "./programs.csv")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            
            for row in csv_reader:
                executor.submit(command.add_version, row)

    command.output(show_commands)