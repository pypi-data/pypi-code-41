from .baseclass import DocumentBaseClass
from ..utils.transformations import latex_escape_regular_text

class TextClass(DocumentBaseClass):
    def __init__(self, text, include_extra_newline_after=False, escape=True):
        self.text = text
        self.include_extra_newline_after = include_extra_newline_after
        self.escape = escape

    def __repr__(self):
        # if self.escape:
        #     repr = latex_escape_regular_text(self.text)
        # else:
        repr = self.text
        if self.include_extra_newline_after:
            repr += "\n\n"
        return repr
