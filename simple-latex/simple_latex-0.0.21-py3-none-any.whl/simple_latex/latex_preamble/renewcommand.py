from .baseclass import PreambleBaseClass


class RenewCommand(PreambleBaseClass):
    def __init__(self, command, definition, arguments=None, optional_default=None):
        self.command = command
        self.arguments = arguments
        self.optional_default = optional_default
        self.definition = definition
        # \renewcommand{cmd}[args][opt]{def}

    def __repr__(self):
        repr = "\\renewcommand"
        repr += "{{\\{}}}".format(self.command)
        if self.arguments is not None:
            repr += "[{}]".format(self.arguments)
        if self.optional_default:
            repr += "[{}]".format(self.optional_default)
        repr += "{{{}}}".format(self.definition)
        return repr + "\n"
