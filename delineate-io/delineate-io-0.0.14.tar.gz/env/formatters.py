import json
from termcolor import colored, cprint
from prettytable import PrettyTable

class JsonFormatter(object):
    
    def format(self, items, show_commands):
        
        jdict = {item.name: item.current for item in items}
        return  json.dumps(jdict, indent=4, sort_keys=True)
        

class TableFormatter(object):
    
    def format(self, items, show_commands):
        
        items.sort(key=lambda item: item.name)

        table = PrettyTable(self.get_headers(show_commands))
        for item in items:
            # current = colored(item.current, 'magenta')
            table.add_row(item.get_values(show_commands))

        return table

    def get_headers(self, show_commands):

        if show_commands:
            return ['Name', 'Current Command', 'Current', 'Latest Command', 'Latest']
        else:
            return ['Name', 'Current', 'Latest']


class XmlFormatter(object):
    
    def format(items, show_commands):
        pass
