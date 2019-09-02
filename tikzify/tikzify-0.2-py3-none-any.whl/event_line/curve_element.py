from abc import abstractmethod

__all__ = ['CurveElement', 'Point', 'Jump', 'Zone']


class CurveElement:

    def __init__(self, latest_key, time, no_absorb=False, **kwargs):
        super().__init__(**kwargs)
        self.time = time
        self.latest_key = latest_key
        self.no_absorb = no_absorb

    # New methods -------------------------------------------------------------
    def latest_time(self):
        return self.time

    def latest_value(self):
        raise NotImplementedError

    # Abstract methods --------------------------------------------------------
    @abstractmethod
    def min_max(self):
        raise NotImplementedError

    @abstractmethod
    def absorb(self, key, time, value):
        raise NotImplementedError

    @abstractmethod
    def draw_points(self, fill):
        raise NotImplementedError


class Point(CurveElement):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    # Implemented virtual methods ---------------------------------------------
    def min_max(self):
        return self.value, self.value

    # Implements method from CurveElement.
    def absorb(self, key, time, value):
        value_range = tuple(sorted([self.value, value]))
        return Zone(latest_key=key,
                    time=self.time,
                    latest_time=time,
                    value_range=value_range,
                    original_value=self.value,
                    latest_value=value)

    # Implements method from CurveElement.
    def draw_points(self, fill):
        yield (self.time, self.value)

    def __repr__(self):
        return f"Point({self.value})"


class Jump(Point):

    def __init__(self, jump_from, **kwargs):
        super().__init__(**kwargs)
        self.jump_from = jump_from

    # Implemented virtual methods ---------------------------------------------
    def min_max(self):
        return min(self.value, self.jump_from), max(self.value, self.jump_from)

    # Implements method from CurveElement.
    def absorb(self, key, time, value):
        value_range = sorted([self.jump_from,
                              self.value,
                              value])
        return Zone(latest_key=key,
                    time=self.time,
                    latest_time=time,
                    value_range=(value_range[0], value_range[2]),
                    original_value=self.jump_from,
                    latest_value=value)

    # Implements method from CurveElement.
    def draw_points(self, fill):
        if self.jump_from != self.value:
            yield (self.time, self.jump_from)
        yield (self.time, self.value)

    def __repr__(self):
        return f"Jump({self.jump_from})"


class Zone(CurveElement):

    def __init__(self,
                 original_value,
                 latest_value,
                 value_range,
                 latest_time,
                 **kwargs):
        super().__init__(**kwargs)
        self.original_value = original_value
        self.latest_value_ = latest_value
        self.latest_time_ = latest_time
        self.value_range = value_range

    def __repr__(self):
        return (f"Zone({self.original_value}, {self.latest_value_}, "
                f"{self.latest_time_}, {self.value_range})")

    # Overridden methods ------------------------------------------------------
    # Overrides method from CurveElement.
    def latest_time(self):
        return self.latest_time_

    def latest_value(self):
        return self.latest_value_

    # Implemented virtual methods ---------------------------------------------
    def min_max(self):
        return self.value_range

    # Implements method from CurveElement.
    def absorb(self, key, time, value):
        return Zone(latest_key=key,
                    time=self.time,
                    latest_time=time,
                    value_range=sorted([min(self.value_range[0], value),
                                        max(self.value_range[1], value)]),
                    original_value=self.original_value,
                    latest_value=value)

    # Implements method from CurveElement.
    def draw_points(self, fill):
        yield (self.time, self.original_value)
        yield (self.time, self.value_range[0])
        yield (self.time, self.value_range[1])
        yield (self.latest_time_, self.latest_value_)
