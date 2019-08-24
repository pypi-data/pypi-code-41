
class Program(object):
    """ """
    
    def __init__(self, config, current = None, latest=None):
        """ """

        self.config = config
        self.name = str(config.name)
        self.current = self.format_version(current)
        self.latest = self.format_version(latest)


    def format_version(self, version):

        if version is not None and version is not "" and version[:1] is not "v":
            version = "v{}".format(version)
        
        return version

    def get_values(self, show_commands):
        
        if show_commands:
            return [self.name, self.config.current_command, 
                self.current, self.config.latest_command, self.latest]
        else:
            return [self.name, self.current, self.latest]