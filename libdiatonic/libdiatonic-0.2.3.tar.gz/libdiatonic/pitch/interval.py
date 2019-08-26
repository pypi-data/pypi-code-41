from .note import Note  # noqa: F401 -- this is used for doctests

__all__ = ('Interval',)


class Interval(object):
    """ Class representing a musical interval

    >>> i1 = Interval(2, Interval.MINOR)
    >>> i1
    Interval(minor 2)
    >>> i2 = Interval.from_half_steps(1)
    >>> i1 == i2
    True
    >>> i3 = Interval(6, Interval.MAJOR)
    >>> i3 != i2
    True
    >>> i3 > i2
    True
    >>> i2 < i3
    True
    >>> i1 + i2
    Interval(major 2)
    >>> i3 - i1
    Interval(minor 6)
    """

    DIMINISHED = 1
    MINOR = 2
    PERFECT = 3
    MAJOR = 4
    AUGMENTED = 5

    _half_step_map = [
        [(1, PERFECT)],
        [(2, MINOR)],
        [(2, MAJOR)],
        [(3, MINOR)],
        [(3, MAJOR)],
        [(4, PERFECT)],
        [(4, AUGMENTED), (5, DIMINISHED)],
        [(5, PERFECT)],
        [(6, MINOR)],
        [(6, MAJOR)],
        [(7, MINOR)],
        [(7, MAJOR)],
    ]

    @classmethod
    def all_modifiers(cls):
        return (
            cls.DIMINISHED, cls.MINOR, cls.PERFECT, cls.MAJOR, cls.AUGMENTED
        )

    @classmethod
    def _modifier_name(cls, modifier):
        for name in ('diminished', 'minor', 'perfect', 'major', 'augmented'):
            if modifier == getattr(cls, name.upper()):
                return name
        raise ValueError('no modifier maps to ' + modifier)

    def __init__(self, number, modifier):
        number = int(number)
        if number < 1 or number > 7:
            raise ValueError('unsupported interval number: ' + str(number))
        self.number = number
        supported_modifier = False
        for key in Interval.all_modifiers():
            if modifier == key:
                supported_modifier = True
        if not supported_modifier:
            raise ValueError('unsupported interval modifier: ' + repr(modifier))
        self.modifier = modifier

    def __repr__(self):
        if self.number == 1:
            desc = 'unison'
        else:
            desc = ' '.join((
                self._modifier_name(self.modifier),
                str(self.number)
            ))
        return '{}({})'.format(self.__class__.__name__, desc)

    @classmethod
    def from_half_steps(cls, half_steps):
        """ Create an Interval object from a number of half steps (mod 12)

        >>> Interval.from_half_steps(5)
        Interval(perfect 4)
        >>> Interval.from_half_steps(13)
        Interval(minor 2)
        """
        half_steps = half_steps % 12
        return cls(*cls._half_step_map[half_steps][0])

    @classmethod
    def from_notes(cls, first, second):
        """ Create an Interval object representing the distance between two notes

        >>> Interval.from_notes(Note('C'), Note('D'))
        Interval(major 2)
        >>> Interval.from_notes(Note('Bb'), Note('Gb'))
        Interval(minor 6)
        >>> Interval.from_notes(Note('A'), Note('A'))
        Interval(unison)
        """
        half_steps = (second.chromatic_index - first.chromatic_index) % 12
        return Interval.from_half_steps(half_steps)

    @property
    def half_steps(self):
        """ Convert an Interval object into its constituent half steps

        >>> Interval(3, Interval.MINOR).half_steps
        3
        >>> Interval.from_half_steps(7).half_steps
        7
        """
        for i in range(len(self._half_step_map)):
            for mapping in self._half_step_map[i]:
                if mapping[0] == self.number and mapping[1] == self.modifier:
                    return i
        raise ValueError('could not determine half steps based on interval ' + repr(self))

    def __eq__(self, other):
        if self.number == other.number and self.modifier == other.modifier:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self.number > other.number:
            return True
        elif self.number == other.number and self.modifier > other.modifier:
            return True
        return False

    def __lt__(self, other):
        if not self.__eq__(other) and not self.__gt__(other):
            return True
        return False

    def __add__(self, other):
        return self.__class__.from_half_steps(self.half_steps + other.half_steps)

    def __sub__(self, other):
        return self.__class__.from_half_steps(self.half_steps - other.half_steps)
