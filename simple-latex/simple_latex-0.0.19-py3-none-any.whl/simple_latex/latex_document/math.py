from .baseclass import DocumentBaseClass

class MathClass(DocumentBaseClass):
    def __init__(self, mathtext, inline=True):
        self.mathtext = mathtext
        self.inline = inline
    
    def __repr__(self):
        if self.inline:
            beginend = "$$"
        else:
            beginend = "$"
        