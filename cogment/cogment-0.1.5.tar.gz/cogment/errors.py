# General aom_framework error
class Error(Exception):
    pass


# Error that occured while configuring the aom_framework
class ConfigError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
