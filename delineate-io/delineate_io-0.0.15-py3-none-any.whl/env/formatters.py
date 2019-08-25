import json
from termcolor import colored, cprint
from prettytable import PrettyTable

class JsonFormatter(object):
    """JsonFormatter formats the program details in Json"""

    def format(self, items, show_commands):
        """Formats the items into Json

        Args:
            items (list): The results of the program assessment
            show_commands (boolean): Indicates if the commands should be shown for debugging
        """  

        jdict = {item.name: item.current for item in items}
        return  json.dumps(jdict, indent=4, sort_keys=True)
        

class TableFormatter(object):
    """TableFormatter formats the program details to a table"""

    def format(self, items, show_commands):
        """Formats the items into a table

        Args:
            items (list): The results of the program assessment
            show_commands (boolean): Indicates if the commands should be shown for debugging
        """  

        items.sort(key=lambda item: item.name)

        table = PrettyTable(self.get_headers(show_commands))
        for item in items:
            # current = colored(item.current, 'magenta')
            table.add_row(item.get_values(show_commands))

        return table


    def get_headers(self, show_commands):
        """Returns the headers to be used for the table

        Args:
            show_commands (boolean): Indicates if the commands should be includes
        """  

        if show_commands:
            return ['Name', 'Current Command', 'Current', 'Latest Command', 'Latest']
        else:
            return ['Name', 'Current', 'Latest']
