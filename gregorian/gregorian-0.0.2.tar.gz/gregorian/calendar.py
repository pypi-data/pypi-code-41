"""
Calendar object
"""
import sortedcontainers
import collections
import datetime
import pandas as pd

import gregorian.utils as utils
import gregorian.internals as internals

RAISE = object()

class Calendar(sortedcontainers.SortedSet):
    def __init__(self, dates=None, key=None):
        """
        Creates a calendar using the optional dates iterable

        Throws
        ------------
        TypeError
            if dates is not an iterable of date-like objects
        """
        if dates is None: 
            dates = []
        else: 
            dates = list(dates)
        if not all([internals.isdatelike(item) for item in dates]):
            raise TypeError("Calendar expected an iterable of date objects")
        super(Calendar, self).__init__(dates)
    
    @property
    def last(self):
        """
        Returns the last date in the calendar

        Throws
        ------------
        KeyError
            if the calendar is empty
        """
        return self[-1]

    @property
    def first(self):
        """
        Returns the first date in the calendar

        Throws
        ------------
        KeyError
            if the calendar is empty
        """
        return self[0]

    @property
    def dates(self):
        """
        Returns the dates as a list
        """
        return list(self)

    def __getitem__(self, value):
        """
        Retrieves a value at a given index
        Retrieves a calendar by a slice
        """
        if isinstance(value, int):
            return super(Calendar, self).__getitem__(value)
        elif isinstance(value, slice):
            if internals.isdatelike(value.start):
                value = slice(self.bisect_left(value.start), value.stop)
            if internals.isdatelike(value.stop):
                value = slice(value.start, self.bisect_right(value.stop))
            return Calendar(super(Calendar, self).__getitem__(value))
        raise KeyError("Invalid index or slice object")

    def filter(self, func=None, *, year=None, semester=None, quarter=None, month=None, week=None, weekday=None):
        """
        Returns a new filtered calendar
        Either pass a filtering function, one or several filtering criterai

        Arguments
        ------------
        func : function, optional
            the filtering function
        year : int, optional
            pass a value to filter dates of the given year only
        semester : int, optional (1 or 2)
            pass a value to filter dates of the given semester only
        quarter : int, optional (1, 2, 3, or 4)
            pass a value to filter dates of the given quarter only
        month : int, optional (1 through 12)
            pass a value to filter dates of the given month only
        week : int, optional (1 through 53)
            pass a value to filter dates of the given week number only
        weekday : int, optional (0 through 6)
            pass a value to filter dates of the given weekday only
            Monday = 0, Tuesday = 1... Sunday = 6

        Return
        ------------
        filtered : Calendar
        """
        if func is not None:
            if not callable(func):
                raise ValueError("Filter accepts either a function, one or several named arguments")
            return Calendar([date for date in self if func(date)])
        if all([arg is None for arg in [year, semester, quarter, month, week, weekday]]):
            raise ValueError("You need to provide one of year, semester, quarter, month, week, weekday")
        if year is not None: 
            dates = list(filter(lambda date: date.year == year, self))
        if semester is not None: 
            dates = list(filter(lambda date: (date.month - 1)//6 + 1 == semester, self))
        if quarter is not None: 
            dates = list(filter(lambda date: (date.month - 1)//3 + 1 == quarter, self))
        if month is not None: 
            dates = list(filter(lambda date: date.month == month, self))
        if week is not None: 
            dates = list(filter(lambda date: date.isocalendar()[1] == week, self))
        if weekday is not None: 
            dates = list(filter(lambda date: date.weekday() == weekday, self))
        return Calendar(dates)

    def weekdays(self):
        """
        Filters out all the weekends
        Assumed to mean Saturdays and Sundays

        Return
        ------------
        filtered : Calendar
        """
        return self.filter(lambda date: date.weekday() not in [5, 6])

    def weekends(self):
        """
        Filters out all the weekdays

        Return
        ------------
        filtered : Calendar
        """
        return self.filter(lambda date: date.weekday() in [5, 6])

    def inverse(self, starting, ending):
        """
        Returns the negative of the calendar, using this calendar as the holiday mask

        Return
        ------------
        inversed : Calendar
        """
        if starting is None: 
            starting = self[0]
        if ending is None: 
            ending = self[-1]
        calendar = Calendar()
        for i in range(1, (ending-starting).days):
            if starting + datetime.timedelta(i) not in self:
                calendar.add(starting + datetime.timedelta(i))
        return calendar

    def dayof(self, date, frequency=None, *, base=1):
        """
        Returns the position of the date in the calendar at a given 
        frequency. By default, base is 1. 

        Return
        ------------
        position : int 
            the index + 1 of the given date in the filtered frequency
        """
        if not internals.isdatelike(date):
            raise ValueError("date should be a date-like object")
        if frequency == None: 
            return self.index(date) + base
        if frequency.lower() in ["y", "year", "a"]:
            return self.filter(year=date.year).index(date) + base
        if frequency.lower() == "semester":
            return self.filter(year=date.year, semester=semester(date)).index(date) + base
        if frequency.lower() in ["m", "month"]:
            return self.filter(year=date.year, month=date.month).index(date) + base
        if frequency.lower() in ["week", "w"]:
            return self.filter(year=date.year, week=date.isocalendar()[1]).index(date) + base
        raise ValueError("Invalid frequency")

    def groupby(self, grouper):
        """
        Returns a calendar-grouper object containing the sub-calendars
        Dates are grouped by the grouper argument
        Grouper argument can be a function or a string frequency
        """
        if isinstance(grouper, str):
            if grouper.lower() in ["w", "week"]:
                return self.groupby(lambda date: (date.year, date.isocalendar()[1]))
            elif grouper.lower() in ["month", "m"]:
                return self.groupby(lambda date: (date.year, date.month))
            elif grouper.lower() in ["q", "quarter"]:
                return self.groupby(lambda date: (date.year, (date.month - 1)//3))
            elif grouper.lower() in ["h", "semester"]:
                return self.groupby(lambda date: (date.year, date.month > 6))
            elif grouper.lower() in ["y", "year"]:
                return self.groupby(lambda date: date.year)
            raise ValueError("Unexpected string")
        if callable(grouper):
            calendars = collections.defaultdict(lambda: Calendar())
            for date in self: 
                calendars[grouper(date)].add(date)
            return Grouper(calendars.values())
        raise ValueError("Expected string or function")

    def fa(self, date, default=RAISE):
        """
        Returns the first date after ("first-after", or "fa")

        Return
        ------------
        date : datetime.date
            the first date following the given date argument
        """
        if date > self[-1]:
            if default == RAISE:
                raise KeyError(f"Out-of-range error: {date} is after last date in the calendar")
            return default
        return self[self.bisect_right(date)]

    def lb(self, date, default=RAISE):
        """
        Returns the last date immediately before ("last-before", or "lb")

        Return
        ------------
        date : datetime.date
            the last date immediately before the given date argument
        """
        if date < self[0]: 
            if default == RAISE:
                raise KeyError(f"Out-of-range error: {date} is before the first date in the calendar")
            return default
        return self[self.bisect_left(date) - 1]

    def snap(self, other, fallback="drop"):
        """
        Snaps this calendar to another
        Date in both calendars are kept
        Dates in this calendar but not in other are either dropped or
        replaced with either the first previous or following date in other

        Return
        ------------
        snapped : Calendar
            the snapped calendar
        """
        if fallback not in ["drop", "previous", "ffill", "next", "bfill"]: 
            raise ValueError("fallback should be one of 'drop', 'previous' or 'next'")
        filtered = Calendar()
        for date in self: 
            if date in other: 
                filtered.add(date)
            else: 
                if fallback == "drop":
                    pass
                elif fallback in ["last", "previous", "ffill"]:
                    filtered.add(other.lb(date))
                elif fallback in ["next", "bfill", "following"]:
                    filtered.add(other.fa(date))
        return filtered
    
    @classmethod
    def generate(cls, *args, **kwargs):
        """
        Creates a new calendar using pandas.date_range

        Returns
        ------------
        calendar : Calendar
            the new calendar
        """
        return Calendar([date.date() for date in pd.date_range(*args, **kwargs)])

    def apply(self, func, *, astype=pd.Series): 
        """
        Apply a function to the calendar

        Returns
        ------------
        mapped : Calendar, pd.Series or other type
            the mapped values
        """
        if not callable(func):
            raise ValueError("Expected function")
        mapped = [func(date) for date in self]
        if all([internals.isdatelike(value) for value in mapped]):
            return Calendar(mapped)
        if astype == pd.Series: 
            return pd.Series(mapped, index=list(self))
        return astype(mapped)

    def astype(self, dtype): 
        """
        Converts the calendar to a specific data-type
        """
        return Calendar([internals.convert(d, dtype) for d in self])

class Grouper: 
    def __init__(self, calendars=None):
        if calendars is None: 
            self.calendars = []
        else:
            if not all([isinstance(calendar, Calendar) for calendar in calendars]): 
                raise TypeError("Expected a list of calendar objects")
            self.calendars = list(calendars)

    def first(self):
        return Calendar([calendar[0] for calendar in self.calendars])

    def last(self):
        return Calendar([calendar[-1] for calendar in self.calendars])

    def __getitem__(self, value):
        if isinstance(value, int):
            return self.calendars[value]
        if isinstance(value, slice):
            return Calendar().union(*self.calendars[value])

    def apply(self, func):
        """
        Apply a function to each sub-calendars
        and merge them back into a single calendar
        """
        if not callable(func): 
            raise ValueError("Expected func to be a callable function")
        calendar = Calendar()
        for cdr in self.calendars: 
            mapped = func(cdr)
            if isinstance(mapped, Calendar):
                calendar = calendar.union(mapped)
            else:
                if not isinstance(mapped, collections.abc.Iterable):
                    mapped = [mapped]
                calendar = calendar.union(Calendar(mapped))
        return calendar

    def __len__(self):
        return len(self.calendars)

