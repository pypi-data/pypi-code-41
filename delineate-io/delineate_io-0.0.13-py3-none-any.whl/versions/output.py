#!/usr/bin/env python

import json
from termcolor import colored, cprint
from prettytable import PrettyTable

class JsonOutput(object):
    """Outputs the program info as Json to either the console or file"""

    def __init__(self, file_name = None):
        """Initializes the Json Outputter

        Args:
            file_name (str): Optional name of the file.
        """

        self.file_name = file_name

    def output(self, items):
        """Outputs the program info as Json

        Args:
            items (list): The list of program info.
        """

        if self.file_name is None:
            self.output_to_console(items)
        else:
            self.output_to_file(items)

    def output_to_console(self, items):
        """Outputs the program info as Json to the console

        Args:
            jdict (dict): The dict of program info.
        """

        table = PrettyTable(['Name', 'Current', 'Latest'])
        for item in items:
            name = item.name
            current = item.current
            latest = item.latest
            if current is None:
                current = colored(item.current, 'magenta')

            table.add_row([name, current, latest])
        
        print()
        print(table)
        print()

    def output_to_file(self, items):
        """Outputs the program info as Json to a file

        Args:
            jdict (dict): The dict of program info.
        """

        jdict = {item.name: item.current for item in items}
        
        with open(self.file_name, 'w') as file:
            json.dump(jdict, file, sort_keys=True, indent=4)

    
