from ..latex_universal import Command
from .baseclass import PreambleBaseClass
from .package import Package
from .newcommand import NewCommand
from .definition import Definition
from .renewcommand import RenewCommand
from .documentclass import Documentclass
from ..utils import transform_dict_to_kv_list
from ..latex_universal.baseclass import UniversalBaseClass


class Preamble:
    def __init__(self, title="", author="", date="", documentclass=Documentclass("article")):
        self.documentclass = documentclass
        self.items = []
        self.author = author
        self.title = title
        self.date = date

    def setDocumentclass(self, documentclass):
        if not isinstance(documentclass, Documentclass):
            raise ValueError
        self.documentclass = documentclass

    def add(self, value):
        if not isinstance(value, PreambleBaseClass) and not isinstance(value, UniversalBaseClass):
            raise ValueError
        self.items.append(value)

    def __repr__(self):
        repr = str(self.documentclass)
        for item in self.items:
            repr += str(item)
        repr += "\\title{{{}}}\n".format(self.title)
        repr += "\\author{{{}}}\n".format(self.author)
        repr += "\\date{{{}}}\n".format(self.date)
        return repr
