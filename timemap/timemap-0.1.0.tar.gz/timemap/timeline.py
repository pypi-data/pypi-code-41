from .utils import DateTimeEncoder
import datetime
import json
from .event import Event
from .report import Report
from typing import List, Union, Callable


class Timeline(object):
    """
    Timeline

    This class defines what events and with which order they have happened over
    a period of time.

    """

    def __init__(self) -> "Timeline":
        super(Timeline, self).__init__()
        self.events = dict()
        self.report = Report()

    def add(
        self, event_filter: Callable = None, event_filter_args: dict = None, **kwargs
    ) -> Union[Event, None]:

        is_valid = True

        try:
            date = kwargs["date"]
        except KeyError:
            raise ValueError("date must be provided")

        try:
            latitude = kwargs["latitude"]
        except KeyError:
            raise ValueError("latitude must be provided")

        try:
            longitude = kwargs["longitude"]
        except KeyError:
            raise ValueError("longitude must be provided")

        try:
            altitude = kwargs["altitude"]
        except KeyError:
            altitude = 0

        event = Event(
            date=date, latitude=latitude, longitude=longitude, altitude=altitude
        )

        if event_filter is not None:

            if event_filter_args is None:
                event_filter_args = dict()

            is_valid = event_filter(event, **event_filter_args)

        if is_valid is True:
            key = date.date().isoformat()
            hhash = date.strftime("%H:%M:%S.%f")
            self.report.add(event.date)

            if key not in self.events:
                self.events[key] = {hhash: None}
            self.events[key][hhash] = event

            return event

    def lookup(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        event_filter: Callable = None,
        event_filter_args: dict = None,
    ) -> None:
        """
        Method to be implemented in specialized class
        """
        raise NotImplementedError

    def summary(self, monthly: bool = False) -> dict:
        """ Loops throw the events and updates the report summary """
        # observations = self.report.daily(self.events)
        if monthly is True:
            print("== monthly summary ==")
            for month in self.report.montlhy:
                month.describe()
        else:
            print("== daily summary ==")
            for day in self.report.daily:
                day.describe()
        return self.report

    def __getitem__(self, key) -> Event:

        date, hhash = key
        return self.events[date][hhash]

    def __iter__(self) -> Event:
        for date, events in self.events.items():
            for item in self.events.items():
                yield item

    def __len__(self) -> int:
        count = 0

        for date, events in self.events.items():
            count = count + len(events)

        return count

    def __str__(self) -> str:
        return str(self.events)
