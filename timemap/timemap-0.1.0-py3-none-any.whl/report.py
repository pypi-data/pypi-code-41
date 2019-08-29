from .utils import DateTimeEncoder
import json
import datetime
from .event import Event
from typing import List


class Breakdown(object):
    """Breakdown"""

    def __init__(self, date: datetime.datetime):
        super(Breakdown, self).__init__()
        self.date = date
        self.seconds = 0
        self.hours = 0
        self.count = 0
        self.previous = None
        self.current = None

    def add(self, date: datetime.datetime, max_interval: int = 1 * 60 * 60):
        self.count += 1
        self.current = date

        if self.previous is not None:
            if self.previous < self.current:
                a = self.current
                b = self.previous
            else:
                a = self.previous
                b = self.current

            interval = (a - b).total_seconds()
            if interval < max_interval:
                self.seconds += interval

        self.hours = self.seconds / (60 * 60)
        self.previous = date

    def describe(self):
        print("date: {}".format(self.date))
        print("  events: {}".format(self.count))
        print("  hours: {}".format(self.hours))

    # TODO: redefine __add__
    def sum(self, other):
        self.hours += other.hours
        self.seconds += other.seconds
        self.count += 1

    def __str__(self) -> str:
        """String representation of object"""
        return json.dumps(self.__dict__, cls=DateTimeEncoder)


class Report(object):
    """Report"""

    def __init__(self):
        super(Report, self).__init__()
        self.clear()

    def clear(self):
        self.start = None
        self.end = None
        self.nb_entries = 0
        self.start_timestamp = None
        self.end_timestamp = None
        self._daily = dict()
        self._monthly = dict()

    def add(self, date: datetime.datetime, descending: bool = True):

        self.nb_entries = self.nb_entries + 1
        timestamp = date.timestamp()

        if self.end is None and self.start is None:
            self.end = date
            self.end_timestamp = timestamp

            self.start = date
            self.start_timestamp = timestamp

        else:
            if date > self.end:
                self.end = date
                self.end_timestamp = timestamp
            else:
                self.start = date
                self.start_timestamp = timestamp

        d = date.date().isoformat()
        if d not in self._daily:
            self._daily[d] = Breakdown(date)
        self._daily[d].add(date)

    @property
    def daily(self):
        for k, v in self._daily.items():
            yield v

    @property
    def montlhy(self):
        self.total_monthly()
        for k, v in self._monthly.items():
            yield v

    def total_daily(self, events: dict):
        self._daily.clear()
        for key, event in events.items():

            if key not in self._daily:
                date = datetime.datetime.strptime(key, "%Y-%m-%d")
                self._daily[key] = Breakdown(date)

            for hhash, event in event.items():
                self._daily[key].add(event.date)

        return self._daily

    def total_monthly(self):
        self._monthly.clear()
        for _, breakdown in self._daily.items():
            date = breakdown.date
            m = "{}{}".format(date.year, date.month)

            if m not in self._monthly:
                self._monthly[m] = Breakdown(date)

            self._monthly[m].sum(breakdown)

        return self._monthly

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self) -> str:
        """String representation of object"""
        return str(self.__dict__)
