class Dependency(dict):
    """Represents the details of a dependency result"""
    
    def __init__(self, config, current, latest):
        """Initializes dependency results
        
        Args:
            config (Config): The config used to retrieve the results
            current (str): The current version installed locally
            latest (str): The latest version available
        """ 

        super().__init__()
        self.__dict__ = self
        self.config = config
        self.name = str(config.name)
        self.current = current
        self.latest = latest