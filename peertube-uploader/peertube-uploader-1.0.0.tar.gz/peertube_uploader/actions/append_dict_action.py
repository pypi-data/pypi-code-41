import argparse


class AppendDictAction(argparse.Action):
    """
    This action simply keeps appending a kvp to a dict each time it's used by argparse
    """

    def __init__(self, option_strings, dest, **kwargs):
        self.key_choices = kwargs.pop("key_choices")
        _help = kwargs.get("help", "")
        if self.key_choices:
            kwargs["help"] = "%s Allowed keys are %s" % (_help, ",".join(self.key_choices))

        nargs = kwargs.get("nargs")
        if nargs != 2:
            raise ValueError("nargs must be 2")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """

        :type parser: argparse.ArgumentParser
        :type namespace: argparse.Namespace
        :param values: A list with 2 elements
        :type values: list[basestring]
        :type option_string: basestring
        """
        if self.key_choices and values[0] not in self.key_choices:
            raise ValueError("%s isn't in key choices: %s" % (values[0], self.key_choices))
        dest = getattr(namespace, self.dest) or dict()
        dest.update(dict([values]))
        setattr(namespace, self.dest, dest)
