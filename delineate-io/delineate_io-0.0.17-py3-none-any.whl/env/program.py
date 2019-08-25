class Program(dict):
    """Represents the results of a program result"""
    
    def __init__(self, config, current, latest):
        """Initializes Program results
        
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