import argparse


class RequiredType(object):
    """
    For use with argparse to make sure a given arg is
    of a given type and not None

    Written originally for use with required options that get their
    default value from the environment.

    argparse's required makes the existence of the option on the
    commandline necessary, which isn't what we want.
    """
    DEFAULT = "__RequiredType__"

    def __init__(self, parser, type_=str):
        self.parser = parser
        self.type_ = type_

    def __call__(self, arg):
        if arg is RequiredType.DEFAULT or arg is None:
            raise argparse.ArgumentTypeError("This is a required parameter")
        return self.type_(arg)
