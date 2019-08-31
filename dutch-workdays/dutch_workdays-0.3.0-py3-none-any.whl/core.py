from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

# Types
from dutch_workdays import easter

Holiday = Tuple[date, str]
Holidays = List[Holiday]
DateInput = Union[date, datetime]


MON, TUE, WED, THU, FRI, SAT, SUN = range(7)


class UnsupportedDateType(Exception):
    pass


def cleaned_date(day: DateInput, keep_datetime: bool = False) -> date:
    """
    Return a "clean" date type.
    * keep a `date` unchanged
    * convert a datetime into a date,
    * convert any "duck date" type into a date using its `date()` method.
    """
    if not isinstance(day, (date, datetime)):
        raise UnsupportedDateType("`{}` is of unsupported type ({})".format(day, type(day)))
    if not keep_datetime:
        if isinstance(day, datetime):
            day = day.date()
    return day


class WesternCalendar:
    """
    General usage calendar for Western countries.
    (chiefly Europe and Northern America)
    """

    WEEKEND_DAYS: Tuple[int, ...] = (SAT, SUN)

    FIXED_HOLIDAYS: Tuple[Tuple[int, int, str], ...] = ((1, 1, "New year"),)

    def __init__(self) -> None:
        self._holidays: Dict[int, Holidays] = {}

    def get_fixed_holidays(self, year: int) -> Holidays:
        """Return the fixed days according to the FIXED_HOLIDAYS class property
        """
        days = []
        for month, day, label in self.FIXED_HOLIDAYS:
            days.append((date(year, month, day), label))
        return days

    def get_variable_days(self, year: int) -> Holidays:
        return []

    def get_calendar_holidays(self, year: int) -> Holidays:
        """
        Get calendar holidays.
        If you want to override this, please make sure that it **must** return
        a list of tuples (date, holiday_name).
        """
        return self.get_fixed_holidays(year) + self.get_variable_days(year)

    def holidays(self, year: int = None) -> Holidays:
        """
        Computes holidays (non-working days) for a given year.
        Return a 2-item tuple, composed of the date and a label.
        """
        if not year:
            year = date.today().year

        if year in self._holidays:
            return self._holidays[year]

        # Here we process the holiday specific calendar
        temp_calendar = tuple(self.get_calendar_holidays(year))

        # it is sorted
        self._holidays[year] = sorted(temp_calendar)
        return self._holidays[year]

    def get_holiday_label(self, day: DateInput) -> Optional[str]:
        """
        Return the label of the holiday, if the date is a holiday
        """
        day = cleaned_date(day)
        return {day: label for day, label in self.holidays(day.year)}.get(day)

    def holidays_set(self, year: int = None) -> Set[date]:
        """
        Return a quick date index (set)
        """
        return set([day for day, label in self.holidays(year)])

    def get_weekend_days(self) -> Tuple[int, ...]:
        """
        Return a list (or a tuple) of weekdays that are *not* working days.
        e.g: return (SAT, SUN,)
        """
        return self.WEEKEND_DAYS

    def is_working_day(
        self,
        day: DateInput,
        extra_working_days: Iterable[DateInput] = None,
        extra_holidays: Iterable[DateInput] = None,
    ) -> bool:
        """
        Return True if it's a working day.
        In addition to the regular holidays, you can add exceptions.
        By providing ``extra_working_days``, you'll state that these dates
        **are** working days.
        By providing ``extra_holidays``, you'll state that these dates **are**
        holidays, even if not in the regular calendar holidays (or weekends).
        Please note that the ``extra_working_days`` list has priority over the
        ``extra_holidays`` list.
        """
        day = cleaned_date(day)
        if extra_working_days:
            extra_working_days = tuple(map(cleaned_date, extra_working_days))
        if extra_holidays:
            extra_holidays = tuple(map(cleaned_date, extra_holidays))

        # Extra lists exceptions
        if extra_working_days and day in extra_working_days:
            return True

        # Regular rules
        if day.weekday() in self.get_weekend_days():
            return False

        return not self.is_holiday(day, extra_holidays=extra_holidays)

    def is_holiday(self, day: DateInput, extra_holidays: Iterable[DateInput] = None) -> bool:
        """
        Return True if it's an holiday.
        In addition to the regular holidays, you can add exceptions.
        By providing ``extra_holidays``, you'll state that these dates **are**
        holidays, even if not in the regular calendar holidays (or weekends).
        """
        day = cleaned_date(day)

        if extra_holidays:
            extra_holidays = tuple(map(cleaned_date, extra_holidays))

        if extra_holidays and day in extra_holidays:
            return True

        return day in self.holidays_set(day.year)

    def add_working_days(
        self,
        day: DateInput,
        delta: int,
        extra_working_days: Iterable[DateInput] = None,
        extra_holidays: Iterable[DateInput] = None,
        keep_datetime: bool = False,
    ) -> date:
        """
        Add `delta` working days to the date.
        You can provide either a date or a datetime to this function that will
        output a ``date`` result. You can alter this behaviour using the
        ``keep_datetime`` option set to ``True``.
        the ``delta`` parameter might be positive or negative. If it's
        negative, you may want to use the ``sub_working_days()`` method with
        a positive ``delta`` argument.
        By providing ``extra_working_days``, you'll state that these dates
        **are** working days.
        By providing ``extra_holidays``, you'll state that these dates **are**
        holidays, even if not in the regular calendar holidays (or weekends).
        Please note that the ``extra_working_days`` list has priority over the
        ``extra_holidays`` list.
        """
        day = cleaned_date(day, keep_datetime)

        if extra_working_days:
            extra_working_days = tuple(map(cleaned_date, extra_working_days))

        if extra_holidays:
            extra_holidays = tuple(map(cleaned_date, extra_holidays))

        days = 0
        temp_day = day
        # Unreachable code?
        # if isinstance(temp_day, datetime) and not keep_datetime:
        #     temp_day = temp_day.date()
        day_added = 1 if delta >= 0 else -1
        delta = abs(delta)
        while days < delta:
            temp_day = temp_day + timedelta(days=day_added)
            if self.is_working_day(
                temp_day, extra_working_days=extra_working_days, extra_holidays=extra_holidays
            ):
                days += 1
        return temp_day

    def sub_working_days(
        self,
        day: DateInput,
        delta: int,
        extra_working_days: Iterable[DateInput] = None,
        extra_holidays: Iterable[DateInput] = None,
        keep_datetime: bool = False,
    ) -> date:
        """
        Substract `delta` working days to the date.
        This method is a shortcut / helper. Users may want to use either::
            cal.add_working_days(my_date, -7)
            cal.sub_working_days(my_date, 7)
        The other parameters are to be used exactly as in the
        ``add_working_days`` method.
        A negative ``delta`` argument will be converted into its absolute
        value. Hence, the two following calls are equivalent::
            cal.sub_working_days(my_date, -7)
            cal.sub_working_days(my_date, 7)
        As in ``add_working_days()`` you can set the parameter
        ``keep_datetime`` to ``True`` to make sure that if your ``day``
        argument is a ``datetime``, the returned date will also be a
        ``datetime`` object.
        """
        delta = abs(delta)
        return self.add_working_days(
            day, -delta, extra_working_days, extra_holidays, keep_datetime=keep_datetime
        )

    def find_following_working_day(self, day: DateInput) -> date:
        """
        Looks for the following working day, if not already a working day.
        **WARNING**: this function doesn't take into account the calendar
        holidays, only the days of the week and the weekend days parameters.
        """
        day = cleaned_date(day)

        while day.weekday() in self.get_weekend_days():
            day = day + timedelta(days=1)
        return day

    @staticmethod
    def get_nth_weekday_in_month(
        year: int, month: int, weekday: int, n: int = 1, start: Optional[DateInput] = None
    ) -> Optional[date]:
        """
        Get the nth weekday in a given month. e.g:
        >>> # the 1st monday in Jan 2013
        >>> Calendar.get_nth_weekday_in_month(2013, 1, MON)
        datetime.date(2013, 1, 7)
        >>> # The 2nd monday in Jan 2013
        >>> Calendar.get_nth_weekday_in_month(2013, 1, MON, 2)
        datetime.date(2013, 1, 14)
        """
        # If start is `None` or Falsy, no need to check and clean
        if start:
            start = cleaned_date(start)

        day = date(year, month, 1)
        if start:
            day = start
        counter = 0
        while True:
            if day.month != month:
                # Don't forget to break if "n" is too big
                return None
            if day.weekday() == weekday:
                counter += 1
            if counter == n:
                break
            day = day + timedelta(days=1)
        return day

    @staticmethod
    def get_last_weekday_in_month(year: int, month: int, weekday: int) -> date:
        """
        Get the last weekday in a given month. e.g:
        >>> # the last monday in Jan 2013
        >>> Calendar.get_last_weekday_in_month(2013, 1, MON)
        datetime.date(2013, 1, 28)
        """
        day = date(year, month, monthrange(year, month)[1])
        while True:
            if day.weekday() == weekday:
                break
            day = day - timedelta(days=1)
        return day

    @staticmethod
    def get_first_weekday_after(day: date, weekday: int) -> date:
        """
        Get the first weekday after a given day. If the day is the same
        weekday, the same day will be returned.
        >>> # the first monday after Apr 1 2015
        >>> Calendar.get_first_weekday_after(date(2015, 4, 1), MON)
        datetime.date(2015, 4, 6)
        >>> # the first tuesday after Apr 14 2015
        >>> Calendar.get_first_weekday_after(date(2015, 4, 14), TUE)
        datetime.date(2015, 4, 14)
        """
        day_delta = (weekday - day.weekday()) % 7
        day = day + timedelta(days=day_delta)
        return day

    def get_working_days_delta(self, start: DateInput, end: DateInput) -> int:
        """
        Return the number of working day between two given dates.
        The order of the dates provided doesn't matter.
        In the following example, there are 5 days, because of the week-end:
        >>> cal = WesternCalendar()  # does not include easter monday
        >>> day1 = date(2018, 3, 29)
        >>> day2 = date(2018, 4, 5)
        >>> cal.get_working_days_delta(day1, day2)
        5
        In France, April 1st 2018 is a holiday because it's Easter monday:
        >>> cal = France()
        >>> cal.get_working_days_delta(day1, day2)
        4
        This method should even work if your ``start`` and ``end`` arguments
        are datetimes.
        """
        start = cleaned_date(start)
        end = cleaned_date(end)

        if start == end:
            return 0

        if start > end:
            start, end = end, start
        # Starting count here
        count = 0
        while start < end:
            start += timedelta(days=1)
            if self.is_working_day(start):
                count += 1
        return count


class ChristianMixin:
    EASTER_METHOD = easter.EASTER_WESTERN
    good_friday_label = "Good Friday"
    whit_sunday_label = "Whit Sunday"
    whit_monday_label = "Whit Monday"
    boxing_day_label = "Boxing Day"

    def get_good_friday(self, year: int) -> date:
        """
        Return the date of the last friday before easter
        """
        sunday = self.get_easter_sunday(year)
        return sunday - timedelta(days=2)

    def get_easter_sunday(self, year: int) -> date:
        """
        Return the date of the easter (sunday) -- following the easter method
        """
        return easter.easter(year, self.EASTER_METHOD)

    def get_easter_monday(self, year: int) -> date:
        """
        Return the date of the monday after easter
        """
        sunday = self.get_easter_sunday(year)
        return sunday + timedelta(days=1)

    def get_ascension_thursday(self, year: int) -> date:
        easter = self.get_easter_sunday(year)
        return easter + timedelta(days=39)

    def get_whit_monday(self, year: int) -> date:
        easter = self.get_easter_sunday(year)
        return easter + timedelta(days=50)

    def get_whit_sunday(self, year: int) -> date:
        easter = self.get_easter_sunday(year)
        return easter + timedelta(days=49)


class Calendar(WesternCalendar, ChristianMixin):
    """
    Netherlands
    """

    FIXED_HOLIDAYS = WesternCalendar.FIXED_HOLIDAYS

    def get_king_queen_day(self, year: int) -> Holiday:
        """
        27 April unless this is a Sunday in which case it is the 26th
        Before 2013 it was called Queensday, falling on
        30 April, unless this is a Sunday in which case it is the 29th.
        """
        if year > 2013:
            if date(year, 4, 27).weekday() != 6:
                return date(year, 4, 27), "King's day"
            else:
                return date(year, 4, 26), "King's day"
        else:
            if date(year, 4, 30).weekday() != 6:
                return date(year, 4, 30), "Queen's day"
            else:
                return date(year, 4, 29), "Queen's day"

    def get_variable_days(self, year: int) -> Holidays:
        days = super().get_variable_days(year)
        days.append(self.get_king_queen_day(year))

        # Christmas Day
        days.append((date(year, 12, 25), "Christmas Day"))

        # Good friday
        days.append((self.get_good_friday(year), self.good_friday_label))

        # Easter sunday
        days.append((self.get_easter_sunday(year), "Easter Sunday"))

        # Easter monday
        days.append((self.get_easter_monday(year), "Easter Monday"))

        # Ascension
        days.append((self.get_ascension_thursday(year), "Ascension Thursday"))

        # Whit sunday
        days.append((self.get_whit_sunday(year), self.whit_sunday_label))

        # Whit monday
        days.append((self.get_whit_monday(year), self.whit_monday_label))

        # Boxing day
        days.append((date(year, 12, 26), self.boxing_day_label))

        return days
