from .baseclass import DocumentBaseClass


class EndClass(DocumentBaseClass):
    def __init__(self, environment):
        self.environment = environment

    def __repr__(self):
        return "\\end{{{}}}\n".format(self.environment)
