class Property:
    def __init__(self, name=None, label=None, typename=None, defval=None):
        self.name = name
        self.label = label
        self.typename = typename
        self.defval = defval

    def __str__(self):
        vals = (self.name, self.label,
                str(self.typename).split("'")[1].replace('tkinter', ''),
                self.defval)
        return 'Property(name="%s" label="%s" typename=%s defval="%s")' % vals

    def __repr__(self):
        return self.__str__()
