class ValidationError:
    """Class to represent a validation error which is created when an error is
    found in the supplied parameters of a class instance"""

    def __init__(self, obj, error):
        self.obj = obj
        self.error = error

    def __str__(self):
        obj = self.obj
        return f'{obj.name}({type(obj)}) reported error: {self.error}'
