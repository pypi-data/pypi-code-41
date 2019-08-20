from ..utils import transform_dict_to_kv_list
from .baseclass import PreambleBaseClass

class Documentclass(PreambleBaseClass):
    def __init__(self, documentclass, options={}):
        self.documentclass = documentclass
        self.options = options

    def __repr__(self):
        repr = "\documentclass"
        if self.options:
            repr += "[{}]".format(transform_dict_to_kv_list(self.options))
        repr += "{{{}}}\n".format(self.documentclass)
        return repr