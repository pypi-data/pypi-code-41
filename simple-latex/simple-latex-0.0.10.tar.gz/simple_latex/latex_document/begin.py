from .baseclass import DocumentBaseClass
from ..utils.transformations import transform_dict_to_kv_list, latex_escape_regular_text


class BeginClass(DocumentBaseClass):
    def __init__(self, environment, optional={}, values=[], escape=True):
        self.environment = environment
        self.optional = optional
        self.values = values
        self.escape = escape

    def __repr__(self):
        repr = "\\begin{{{}}}".format(self.environment)
        if self.optional:
            repr += "[{}]".format(transform_dict_to_kv_list)
        for value in self.values:
            if self.escape:
                esc_value = latex_escape_regular_text(value)
                repr += "{{{}}}".format(esc_value)
            else:
                repr += "{{{}}}".format(value)
        return repr + "\n"
