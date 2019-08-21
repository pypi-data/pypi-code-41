"""
Author: qiacai
"""

from ada_core import utils


class Entry(object):

    def __init__(self, timestamp=0, value=0.0):
        self.timestamp = int(timestamp)
        self.value = float(value)

    def __repr__(self):
        return 'Entry<timestamp={0}, value={1}>'.format(repr(self.timestamp), repr(self.value))

    def __str__(self):
        return 'Entry(timestamp={0}, value={1})'.format(repr(self.timestamp), repr(self.value))

    # def __bool__(self):
    #     return True if self.value else False

    def getValue(self):
        return self.value

    def getTimestamp(self):
        return self.timestamp

    def equals(self, other):
        if not isinstance(other, Entry):
            return False
        if self.timestamp != other.timestamp or self.value != other.value:
            return False
        else:
            return True

    def eq(self, other):
        if isinstance(other, Entry):
            if self.timestamp != other.timestamp:
                raise ValueError("Can only compare identically-labeled entry")
            else:
                return Entry(self.timestamp, True) if self.value == other.value else Entry(self.timestamp, False)
        elif isinstance(other, int) or isinstance(other, float):
            return Entry(self.timestamp, True) if self.value == other else Entry(self.timestamp, False)
        else:
            raise ValueError("only support compare with numeric value or entry")

    def __eq__(self, other):
        return self.eq(other)

    def ge(self, other):
        if isinstance(other, Entry):
            if self.timestamp != other.timestamp:
                raise ValueError("Can only compare identically-labeled entry")
            else:
                return Entry(self.timestamp, True) if self.value >= other.value else Entry(self.timestamp, False)
        elif isinstance(other, int) or isinstance(other, float):
            return Entry(self.timestamp, True) if self.value >= other else Entry(self.timestamp, False)
        else:
            raise ValueError("only support compare with numeric value or entry")

    def __ge__(self, other):
        return self.ge(other)

    def greaterThanOrEquals(self, other):
        return True if self.ge(other).value > 0 else False

    def gt(self, other):
        if isinstance(other, Entry):
            if self.timestamp != other.timestamp:
                raise ValueError("Can only compare identically-labeled entry")
            else:
                return Entry(self.timestamp, True) if self.value > other.value else Entry(self.timestamp, False)
        elif isinstance(other, int) or isinstance(other, float):
            return Entry(self.timestamp, True) if self.value > other else Entry(self.timestamp, False)
        else:
            raise ValueError("only support compare with numeric value or entry")

    def __gt__(self, other):
        return self.gt(other)

    def greaterThan(self, other):
        return True if self.gt(other).value > 0 else False

    def le(self, other):
        if isinstance(other, Entry):
            if self.timestamp != other.timestamp:
                raise ValueError("Can only compare identically-labeled entry")
            else:
                return Entry(self.timestamp, True) if self.value <= other.value else Entry(self.timestamp, False)
        elif isinstance(other, int) or isinstance(other, float):
            return Entry(self.timestamp, True) if self.value <= other else Entry(self.timestamp, False)
        else:
            raise ValueError("only support compare with numeric value or entry")

    def __le__(self, other):
        return self.le(other)

    def lessThanOrEquals(self, other):
        return True if self.le(other).value > 0 else False

    def lt(self, other):
        if isinstance(other, Entry):
            if self.timestamp != other.timestamp:
                raise ValueError("Can only compare identically-labeled entry")
            else:
                return Entry(self.timestamp, True) if self.value < other.value else Entry(self.timestamp, False)
        elif isinstance(other, int) or isinstance(other, float):
            return Entry(self.timestamp, True) if self.value < other else Entry(self.timestamp, False)
        else:
            raise ValueError("only support compare with numeric value or entry")

    def __lt__(self, other):
        return self.lt(other)

    def lessThan(self, other):
        return True if self.lt(other).value > 0 else False

    def add(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value + other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value + other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __add__(self, other):
        return self.add(other)

    def radd(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value + other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value + other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __radd__(self, other):
        return self.radd(other)

    def sub(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value - other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value - other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __sub__(self, other):
        return self.sub(other)

    def rsub(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, other - self.value)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, other.value - self.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __rsub__(self, other):
        return self.rsub(other)

    def mul(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value * other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value * other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __mul__(self, other):
        return self.mul(other)

    def rmul(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value * other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value * other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __rmul__(self, other):
        return self.mul(other)

    def truediv(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value / other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value / other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __truediv__(self, other):
        return self.truediv(other)

    def rtruediv(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, other / self.value)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, other.value / self.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __rtruediv__(self, other):
        return self.rtruediv(other)

    def floordiv(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value // other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value // other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __floordiv__(self, other):
        return self.floordiv(other)

    def rfloordiv(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, other // self.value)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, other.value // self.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __rfloordiv__(self, other):
        return self.rfloordiv(other)

    def mod(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value % other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value % other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __mod__(self, other):
        return self.mod(other)

    def rmod(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, other % self.value)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, other.value % self.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __rmod__(self, other):
        return self.rmod(other)

    def pow(self, other):

        if isinstance(other, float) or isinstance(other, int):
            return Entry(self.timestamp, self.value ** other)
        elif isinstance(other, Entry):
            if self.timestamp == other.timestamp:
                return Entry(self.timestamp, self.value ** other.value)
            else:
                raise ValueError('the timestamp of these two enries not match')
        else:
            raise ValueError("only support numeric value or entry type")

    def __pow__(self, other):
        return self.pow(other)

    def __round__(self, ndigits=0):
        return Entry(self.timestamp, round(self.value, ndigits))

    def __abs__(self):
        return Entry(self.timestamp, abs(self.value))

    def __neg__(self):
        return Entry(self.timestamp, -self.value)

    def __pos__(self):
        return Entry(self.timestamp, +self.value)

    def timeOffset(self, offset_window=0, timezone=None):
        try:
            offset_window = int(offset_window)
            offset_window = str(offset_window) + 's'
        except ValueError:
            pass
        timestamp_set = utils.window2timestamplite(self.value, offset_window, timezone, always_sub=False)
        return Entry(timestamp_set, self.value)