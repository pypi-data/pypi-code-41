from termcolor import colored, cprint

class Value(dict):
    """Base class for all value classes""" 

    def init(self, value, coloured):
        """Initializes the class and calls the __init__ of the dict

        Args:
            value (str): The value
            coloured (str): The coloured value
        """

        super().__init__()
        self.__dict__ = self

        self.value = value
        self.coloured_value = coloured


    def get_value(self, in_colour=False):
        """Retrieves the value correctly

        Args:
            in_colour (boolean): Indicates if the coloured value should be returned
        """

        if in_colour:
            return self.coloured_value
        else:
            return self.value


class Version(Value):
    """Version represents a version"""

    def __init__(self, value):
        """Initializes the Version

        Args:
            value (str): Value that represents the version
        """

        value = self.format(value)
        self.init(value, value)


    def format(self, value):
        """Formats a version number
        
        Args:
            value (str): The raw version number before formatting
        """ 

        if value[:1] is not "v":
            value = "v{}".format(value)
        
        return value


class NotInstalled(Value):
    """NotInstalled indicates that the dependency is not installed"""

    def __init__(self):
        """Initializes the NotInstalled"""

        value = "Not Installed"
        self.init(value, colored(value, 'magenta'))
        

class Error(Value):
    """Error indicates an error"""

    def __init__(self):
        """Initializes the Error"""

        value = "Error"
        self.init(value, colored(value, 'red'))