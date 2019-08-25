
class Program(object):
    """Represents the results of a program result"""
    
    def __init__(self, config, current, latest):
        """Initializes Program results
        
        Args:
            config (Config): The config used to retrieve the results
            current (str): The current version installed locally
            latest (str): The latest version available
        """ 

        self.config = config
        self.name = str(config.name)
        self.current = self.format_version(current)
        self.latest = self.format_version(latest)


    def format_version(self, version):
        """Formats a version number
        
        Args:
            version (str): The raw version number before formatting
        """ 

        if version is not None and version is not "" and version[:1] is not "v":
            version = "v{}".format(version)
        
        return version


    def get_values(self, show_commands):
        """Retrieves the values for the program
        
        Args:
            show_commands (boolean): Determines if the commands should be shown
        """ 

        if show_commands:
            return [self.name, self.config.current_command, 
                self.current, self.config.latest_command, self.latest]
        else:
            return [self.name, self.current, self.latest]