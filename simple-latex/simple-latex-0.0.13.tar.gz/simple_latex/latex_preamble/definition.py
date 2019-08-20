from .baseclass import PreambleBaseClass


class Definition(PreambleBaseClass):
    def __init__(self, command, replacement, parameter_string=None):
        super()
        self.command = command
        self.parameter_string = parameter_string
        self.replacement = replacement

    def __repr__(self):
        repr = "\\def \\{} ".format(self.command)
        if self.parameter_string:
            repr += self.parameter_string
        repr += "{{{}}}\n".format(self.replacement)
        return repr