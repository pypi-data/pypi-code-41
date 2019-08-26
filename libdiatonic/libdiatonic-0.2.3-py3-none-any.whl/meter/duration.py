from fractions import Fraction

__all__ = ('TimeUnit', 'Duration')


class TimeUnit(int):
    """ int with some extra properties and checking

    >>> TimeUnit(1)
    TimeUnit(1)
    >>> TimeUnit(4).ratio
    '1/4'
    """

    def __new__(cls, denominator):
        if denominator == 1 or (float(denominator) / 2.0).is_integer():
            return int.__new__(cls, denominator)
        raise ValueError('expected denominator to be 1 or a power of 2, got ' + str(denominator))

    @property
    def ratio(self):
        return '1/' + str(self)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self))


WHOLE = TimeUnit(1)
HALF = TimeUnit(2)
QUARTER = TimeUnit(4)
EIGHTH = TimeUnit(8)
SIXTEENTH = TimeUnit(16)
THIRTYSECOND = TimeUnit(32)
SIXTYFOURTH = TimeUnit(64)


class Duration(object):
    """ Essentially a two-length named tuple (count, unit) with some sanity checking

    >>> d1 = Duration(4, 4)
    >>> d1
    Duration(4/4)
    >>> d2 = Duration('6/8')
    >>> d2
    Duration(6/8)
    >>> d1 > d2
    True
    >>> d2 * 3
    Duration(18/8)
    """

    def __init__(self, *args):
        bad_args_msg = 'expected Duration("int/int") or Duration(int, int)'
        if len(args) == 0 or len(args) > 2:
            raise ValueError(bad_args_msg)
        if len(args) == 1:
            if args[0] == 0:
                count = 0
                unit = 4
            else:
                if isinstance(args[0], (float, int)):
                    raise ValueError('tried to instantiate duration with a numeric type, '
                                     'perhaps you forgot some quotes (eg. 4/4 vs "4/4")')
                try:
                    count, unit = args[0].split('/')
                except ValueError:
                    raise ValueError(bad_args_msg)
        else:
            count, unit = args
        count = int(count)
        unit = TimeUnit(int(unit))
        if count < 0:
            raise ValueError('expected count to be a non-negative integer, got ' + str(count))
        self.count = count
        self.unit = unit

    def __str__(self):
        return '{}/{}'.format(self.count, self.unit)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, str(self))

    @classmethod
    def _same_type_or_raise(cls, other):
        if not isinstance(other, cls):
            raise TypeError('expected {}, got {}'.format(cls, type(other)))

    def _get_common_counts(self, other):
        self._same_type_or_raise(other)
        left_count, left_unit = self.count, self.unit
        right_count, right_unit = other.count, other.unit
        if left_unit > right_unit:
            right_count = int(right_count * (left_unit / right_unit))
            common_unit = left_unit
        elif right_unit > left_unit:
            left_count = int(left_count * (right_unit / left_unit))
            left_unit = right_unit
            common_unit = right_unit
        else:
            common_unit = left_unit
        return left_count, right_count, common_unit

    def __add__(self, other):
        left_count, right_count, unit = self._get_common_counts(other)
        return self.__class__(left_count + right_count, unit)

    def __sub__(self, other):
        left_count, right_count, unit = self._get_common_counts(other)
        return self.__class__(left_count - right_count, unit)

    def __eq__(self, other):
        self._same_type_or_raise(other)
        return self.count == other.count and self.unit == other.unit

    def __ne__(self, other):
        self._same_type_or_raise(other)
        return not self.__eq__(other)

    def _get_fractions(self, other):
        self._same_type_or_raise(other)
        self_fraction = Fraction(self.count, self.unit)
        other_fraction = Fraction(other.count, other.unit)
        return self_fraction, other_fraction

    def __gt__(self, other):
        self_fraction, other_fraction = self._get_fractions(other)
        return self_fraction > other_fraction

    def __ge__(self, other):
        if self > other or self == other:
            return True
        return False

    def __lt__(self, other):
        self_fraction, other_fraction = self._get_fractions(other)
        return self_fraction < other_fraction

    def __le__(self, other):
        if self < other or self == other:
            return True
        return False

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError('expected int for duration multiplication, got ' + type(other))
        return self.__class__(self.count * other, self.unit)

    def issimilar(self, other):
        self_fraction, other_fraction = self._get_fractions(other)
        return self_fraction == other_fraction
