from .duration import Duration

__all__ = ('MeasureBar', 'MeasureObject', 'Measure')


class MeasureBar(object):
    SINGLE = 0
    DOUBLE = 1
    SECTION_OPEN = 10
    SECTION_CLOSE = 11
    REPEAT_OPEN = 20
    REPEAT_CLOSE = 21

    @classmethod
    def all(cls):
        ret = []
        for attr in dir(cls):
            if attr.upper() == attr:
                ret.append(attr)
        return ret

    @classmethod
    def isvalid(cls, value):
        for valid_value in cls.all():
            return True
        return False


class MeasureObject(object):
    """ give an arbitrary object a duration

    >>> MeasureObject('C', '1/4')
    MeasureObject('C', Duration(1/4))
    """

    def __init__(self, obj, duration):
        if not isinstance(duration, Duration):
            duration = Duration(duration)
        self.duration = duration
        self.obj = obj

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, repr(self.obj), repr(self.duration))


class MeasureAttrStruct(object):

    def __init__(self):
        self.open = self.close = None


class MeasureBarsStruct(MeasureAttrStruct):

    def __init__(self):
        self.open = self.close = MeasureBar.SINGLE

    @property
    def open(self):
        return self._open

    @open.setter
    def open(self, value):
        if not MeasureBar.isvalid(value):
            raise ValueError('expected valid MeasureBar.*, got ' + value)
        self._open = value

    @property
    def close(self):
        return self._close

    @close.setter
    def close(self, value):
        if not MeasureBar.isvalid(value):
            raise ValueError('expected valid MeasureBar.*, got ' + value)
        self._close = value


class Measure(list):
    """ list with some additional checks

    >>> m = Measure('4/4')
    >>> m.isempty()
    True
    >>> m.append(MeasureObject('C', '3/4'))
    >>> m.utilization
    Duration(3/4)
    >>> m.append('G', '1/4')
    >>> m
    Measure(Duration(4/4), [MeasureObject('C', Duration(3/4)), MeasureObject('G', Duration(1/4))])
    >>> m.isfull()
    True
    """

    def __init__(self, duration):
        if not isinstance(duration, Duration):
            duration = Duration(duration)
        self.duration = duration
        self.bars = MeasureBarsStruct()

    def __repr__(self):
        return '{}({}, [{}])'.format(self.__class__.__name__, repr(self.duration),
                                     ', '.join([repr(o) for o in self]))

    @property
    def utilization(self):
        if len(self) == 0:
            return Duration(0)
        ret = self[0].duration
        for duration in [mo.duration for mo in self[1:]]:
            ret += duration
        return ret

    def isempty(self):
        return self.utilization == Duration(0)

    def isfull(self):
        return self.utilization.issimilar(self.duration)

    @property
    def remainder(self):
        if self.isempty():
            return self.duration
        if self.isfull():
            return Duration(0)
        return self.duration - self.utilization

    def append(self, *args):
        obj = MeasureObject(*args) if len(args) == 2 else args[0]
        if not isinstance(obj, MeasureObject):
            raise TypeError('expected MeasureObject when appending to Measure, got ' + type(obj))
        utilization_before = self.utilization
        utilization_after = (
            utilization_before + obj.duration if not self.isempty() else obj.duration)
        if utilization_after > self.duration:
            remaining_duration = (
                self.duration - utilization_before if not self.isfull() else None)
            raise ValueError('cannot add MeasureObject of duration {}, not enough room in Measure '
                             '(max: {}, remaining: {})'.format(
                                 obj.duration, self.duration, remaining_duration))
        super(Measure, self).append(obj)
