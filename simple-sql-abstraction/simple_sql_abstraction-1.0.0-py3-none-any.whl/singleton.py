class Singleton:
    """
    A class used to make Singletons instances

    Attributes
    ----------
    instance : ?
        instance of the class that is decendent from this

    Methods
    -------
    display()
        Prints the class values
    """
    instance = None

    def __new__(classtype, *args, **kwargs):
        __classtype = classtype
        if not isinstance(classtype.instance, classtype):
            classtype.instance = object.__new__(classtype)
        return classtype.instance

    def __init__(self, name=None):
        self.name = name

    def display(self):
        print(self.name, id(self), type(self))
