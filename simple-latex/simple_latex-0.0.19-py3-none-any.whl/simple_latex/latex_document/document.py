from ..latex_universal.baseclass import UniversalBaseClass
from .baseclass import DocumentBaseClass
from .begin import BeginClass
from .end import EndClass
from .math import MathClass


class Document:
    def __init__(self):
        self.indentation = 0
        self.items = []

    def add(self, item):
        if not isinstance(item, DocumentBaseClass) and not isinstance(item, UniversalBaseClass):
            raise ValueError
        if isinstance(item, BeginClass):
            self.items.append((item, self.indentation))
            self.indentation += 4
        elif isinstance(item, EndClass):
            self.indentation -= 4
            self.items.append((item, self.indentation))
        else:
            self.items.append((item, self.indentation))

    def __repr__(self):
        repr = "\\begin{document}\n"
        for item in self.items:
            repr += " "*item[1] + str(item[0])
        repr += "\\end{document}\n"
        return repr
