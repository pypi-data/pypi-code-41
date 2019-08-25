from termcolor import colored, cprint

class VersionValue(dict):

    def __init__(self, value):
        
        super().__init__()
        self.__dict__ = self

        self.value = self.add_prefix(value)
        self.coloured_value = self.value

    def add_prefix(self, value):
        """Formats a version number
        
        Args:
            version (str): The raw version number before formatting
        """ 

        if value is not None and value is not "" and value[:1] is not "v":
            value = "v{}".format(value)
        
        return value
    
    def get_value(self, in_colour):

        if in_colour:
            return self.coloured_value
        else:
            return self.value

class NotInstalledValue(dict):
    
    def __init__(self):
        
        super().__init__()
        self.__dict__ = self

        self.value = "Not Installed"
        self.coloured_value = colored(self.value, 'magenta')

    def get_value(self, in_colour):

        if in_colour:
            return self.coloured_value
        else:
            return self.value

class ErrorValue(dict):
    
    def __init__(self, value):
        
        super().__init__()
        self.__dict__ = self
        
        self.value = "Error"
        self.coloured_value = colored(self.value, 'red')

    def get_value(self, in_colour):

        if in_colour:
            return self.coloured_value
        else:
            return self.value