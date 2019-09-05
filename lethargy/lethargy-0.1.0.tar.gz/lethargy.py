import sys
from copy import copy

__version__ = "0.1.0"
__all__ = ("OptionError", "ArgsError", "MissingOption", "Opt", "Argv", "argv")


class OptionError(Exception):
    pass


class ArgsError(OptionError):
    pass


class MissingOption(OptionError):
    pass


def dashed(text) -> str:
    string = str(text).strip()
    if not string:
        return ""
    dashes = "--" if len(string) > 1 else "-"
    return "{}{}".format(dashes, text)


def kebabcase(text) -> str:
    return "-".join(str(text).split())


def greedy(amount):
    return amount in GREEDY_VALUES


def take(start, offset, lst):
    """Remove and return the values from indices start to offset

    This function will include the name of option itself in the returned list.
    Raises OptionError if the value did not have the expected number of args.
    """
    end = start + offset
    out = lst[start:end]
    del lst[start:end]
    return out


GREEDY_VALUES = frozenset([..., any, greedy, "*"])


class Opt:
    """Easily handle options by mutating the list of arguments

    `names` can include strings with whitespace. Everything will become
    --skewered-kebab-case. No input validation will be performed.
    """

    def __init__(self, *names):
        if names:
            self.names = set(map(lambda x: dashed(kebabcase(str(x))), names))
        else:
            self.names = set()
        self.arg_amt = 0

    def __iter__(self):
        return iter(self.names)

    def __copy__(self):
        new = self.__class__()
        new.names = copy(self.names)
        new.arg_amt = self.arg_amt
        return new

    def __str__(self):
        if not self.names:
            return ""

        names = "|".join(self.names)

        if greedy(self.arg_amt):
            vals = "[value]..."
        elif self.arg_amt > 0:
            vals = " ".join("<value>" for _ in range(self.arg_amt))
        else:
            vals = None

        if vals is not None:
            return "{} {}".format(names, vals)
        else:
            return names

    def __repr__(self):
        qname = self.__class__.__qualname__
        mapped = map(lambda x: repr(x.replace('-', ' ').strip()), self)
        names = ', '.join(mapped)
        return "<{}({}).takes({})>".format(qname, names, self.arg_amt)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.names == other.names and self.arg_amt == other.arg_amt
        else:
            return NotImplemented

    def takes(self, n):
        """Define how many arguments the option takes (allows chaining)

        Using a greedy value (..., any, lethargy.greedy, "*") as the number
        of arguments will consume all values after the option.
        """
        self.arg_amt = n
        return self

    def new_takes(self, n):
        """Create an identical instance and define its number of arguments"""
        return copy(self).takes(n)

    def find_in(self, args):
        """Return the index of args for the first argname of this instance"""
        for name in self:
            try:
                return args.index(name)
            except ValueError:
                continue
        return None

    def take_flag(self, args) -> bool:
        """Test whether the args contain the option, and remove it if True"""
        idx = self.find_in(args)
        if idx is not None:
            args.pop(idx)
            return True
        else:
            return False

    def take_args(self, args, default=None, raises=False):
        """Retreive this option's arguments from args and mutate on success"""
        amt = self.arg_amt

        # Taking 0 arguments will do nothing, better to use take_flag
        if amt == 0:
            msg = "{} takes 0 arguments - did you mean to use `take_flag`?"
            raise ArgsError(msg.format(self))

        # Is this option in the list?
        index = self.find_in(args)

        # Option not found in args, skip the remaining logic and return the
        # default value. No list mutation will occur
        if index is None:
            if raises:
                msg = "{} was not found in {}"
                raise MissingOption(msg.format(self, args))

            # The different behaviours for defaulting (fairly simple to
            # understand). Basically: if the default is None, handle it
            # specially, otherwise just return what the user wants.
            if greedy(amt):
                return [] if default is None else default
            elif default is None and amt != 1:
                return [default] * amt
            else:
                return default

        # Prepare values to mutate the list and take the arguments.
        # `take` needs a starting index, an offset, and a list to mutate.
        if greedy(amt):
            # Number of indices succeeding the starting index
            offset = len(args) - index
        else:
            # Why the +1? Because if we used 1 as the offset, then from
            # ['--test', 'value'], only '--test' would be taken
            offset = amt + 1

            # Calling `take` will mutate the list, but if the option doesn't
            # have any arguments then that mutation will have been for nothing
            # and it may mess up other state. Raising before anything bad
            # happens will either halt execution or allow the user to recover,
            # without ruining other state.
            end_idx = index + offset
            if end_idx > len(args):
                n_found = 1 + len(args) - end_idx  # start at 1, not 0
                args_or_arg = "argument" if amt == 1 else "arguments"
                msg = "expected {} {} for '{}', found {}"
                raise ArgsError(msg.format(amt, args_or_arg, self, n_found))

        # The list mutation happens here. If anything goes wrong, this is
        # probably why.
        taken = take(index, offset, args)[1:]

        # Return the value(s) taken
        #             1 -> single value
        #  2+ or greedy -> list of values
        # anything else -> raise error (wtf happened??)
        if amt == 1:
            # Return the value as itself, no list.
            return taken[0]
        # the greedy values don't support __gt__, so if amt is greedy then
        # this will short circuit and it won't fail!
        elif greedy(amt) or amt > 1:
            # Return the taken values as a list
            return taken
        else:
            # amt is not valid - who even knows how we even got to this point.
            # if anyone ever manages to trigger this, please let me know how!
            msg = "{!r} was found, but {!r} arguments could not be retreived."
            raise ArgsError(msg.format(self, amt))

    @staticmethod
    def is_short(text):
        try:
            return text.startswith("-") and text[1] != "-" and len(text) == 2
        except IndexError:
            return False

    @staticmethod
    def is_long(text):
        try:
            return text.startswith("--") and text[2] != "-" and len(text) > 2
        except IndexError:
            return False


class _ListSubclass(list):
    """A type that implements methods in a subclass-neutral way"""

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            try:
                return self.__class__(result)
            except TypeError:
                pass
        return result

    def __add__(self, rhs):
        return self.__class__(list.__add__(self, rhs))


class Argv(_ListSubclass):
    """Provides helper methods for working with options and arguments"""

    def opts(self):
        """Yield tuples containing the index and name of each option"""
        for index, item in enumerate(self):
            if Opt.is_long(item):
                yield index, item
            elif Opt.is_short(item):
                yield index, item

    @classmethod
    def from_argv(cls):
        return cls(copy(sys.argv))


# Lethargy provides its own argv so you don't have to also import sys. The
# additional functionality provided by its type lets you more easily create a
# custom solution.
argv = Argv.from_argv()
