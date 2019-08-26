import json
from prettytable import PrettyTable

class JsonFormatter(object):
    """JsonFormatter formats the program details in Json"""

    def format(self, items):
        """Formats the items into Json

        Args:
            items (list): The results of the program assessment
        """
        return  json.dumps(items, indent=4, sort_keys=True)
        

class TableFormatter(object):
    """TableFormatter formats the program details to a table"""

    def __init__(self, in_colour=False):

        self.in_colour = in_colour

    def format(self, items):
        """Formats the items into a table

        Args:
            items (list): The results of the program assessment
        """  

        items.sort(key=lambda item: item.name)

        table = PrettyTable(['Name','Brew', 'Current', 'Latest'])
        for item in items:
            table.add_row(self.get_values(item))

        return table.get_string()


    def get_values(self, item):
        """Retrieves the values for the program
        
        Args:
            item (Dependency): The item to get the values for
        """ 

        return [item.name, 
            "Yes",
            item.current.get_value(self.in_colour), 
            ""]
            # item.latest.get_value(self.in_colour)]