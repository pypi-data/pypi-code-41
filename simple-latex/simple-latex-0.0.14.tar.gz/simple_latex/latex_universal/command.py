from .baseclass import UniversalBaseClass
from ..utils import transform_dict_to_kv_list, latex_escape_regular_text

class Command(UniversalBaseClass):
    def __init__(self, command, optional={}, parameters={}, values=[], text=None, starred=False, escapeValues=True, escapeText=True):
        self.command = command
        self.values = values
        self.text = text
        self.starred = starred
        self.parameters = parameters
        self.optional = optional
        self.escapeText = escapeText
        self.escapeValues = escapeValues

    def __repr__(self):
        """
            Preamble.add(Command("lawyers", None, "h", ["c", "d"]))
            \lawyers[h]{c}{d}
            Preamble.add(Command("titleformat", "\\chapter", "display", ["\\normalfont\\huge\\bfseries", "", "0pt", "\\Huge"]))
            \titleformat{\chapter}[display]{\normalfont\huge\bfseries}{}{0pt}{\Huge}
            \titlespacing*{\chapter}{0pt}{-30pt}{20pt}
        """
        repr = "\\{}".format(self.command)
        if self.starred:
            repr += "*"
        if self.optional:
            repr += "{{{}}}".format(self.optional)
        if self.parameters:
            repr += "[{}]".format(transform_dict_to_kv_list(self.parameters))
        if self.values:
            for value in self.values:
                if self.escapeValues:
                    replaced = latex_escape_regular_text(value)
                    print(replaced)
                    print(type(replaced))
                    repr += "{{{}}}".format(replaced)
                else:
                    repr += "{{{}}}".format(value)
        if self.text is not None:
            if self.escapeText:
                repr += " {}".format(latex_escape_regular_text(self.text))
            else:
                repr += " {}".format(self.text)
        return repr + "\n"
