from ..timeline import Timeline
from ..event import Event
from ..error import DateEndError
from typing import Any, Callable, Union

import ijson
import datetime


class Takeout(Timeline):
    """
    Takeout

    GMAPS specialization of the timeline interface

    """

    SEARCHING = 1
    START_EVENT = 2
    END_EVENT = 3

    def __init__(self, filepath: str):
        super(Takeout, self).__init__()

        self.filepath = filepath
        self._fd = None
        self._parse = None
        self.load()

    def add(
        self, event_filter: Callable = None, event_filter_args: dict = None, **kwargs
    ) -> Union[Event, None]:

        event = super().add(event_filter, event_filter_args, **kwargs)
        if event is not None:
            try:
                event.accuracy = kwargs["accuracy"]
            except KeyError:
                pass
        return event

    def load(self):
        self.report.clear()
        if self._fd:
            self._fd.close()
        self._fd = open(self.filepath, "r")
        self._parser = ijson.parse(self._fd)

    def item_start(self, prefix: str, event: str, value: Any, storage: dict = None):

        if prefix == "locations.item" and event == "start_map":
            return True
        else:
            return False

    def item_end(self, prefix: str, event: str, value: Any, storage: dict = None):

        if prefix == "locations.item" and event == "end_map":
            return True

        return False

    def item_acquire(
        self,
        prefix: str,
        event: str,
        value: Any,
        storage: dict,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
    ):

        if prefix == "locations.item.timestampMs":
            date = float(value.encode()) / 1e3
            date = datetime.datetime.fromtimestamp(date)

            # check if time is legal
            if start is not None:
                if date < start:
                    return False
            if end is not None:
                if date > end:
                    return False

            storage["date"] = date

        if prefix == "locations.item.latitudeE7":
            storage["latitude"] = value * 1e-7

        elif prefix == "locations.item.longitudeE7":
            storage["longitude"] = value * 1e-7

        elif prefix == "locations.item.altitude":
            storage["altitude"] = value

        elif prefix == "locations.item.accuracy":
            storage["accuracy"] = value

        elif prefix in "locations.item.activity":
            pass

        return True

    def browse(self, start=None):
        """ Quick overview of the contents the location history contents """

        self.report.clear()

        for prefix, event, value in self._parser:
            if prefix == "locations.item.timestampMs":
                timestamp = float(value.encode()) / 1e3
                date = datetime.datetime.fromtimestamp(timestamp)
                self.report.add(date)

        return self.report

    def lookup(
        self,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        event_filter: Callable = None,
        event_filter_args: dict = None,
    ):
        """
            Performs a search over the events and creates an object for valid ones

            By default the validity of the objects is set according to the start
            and end date. Optionally, a filter callable can be provided.

            event_filter: when true, the object is considered valid
            evnet_filter_args: additional arguments to pass to the filter function
        """

        storage = dict()
        self.state = self.SEARCHING

        for prefix, event, value in self._parser:

            if self.state == self.SEARCHING:
                if self.item_start(prefix, event, value, storage):
                    self.state = self.START_EVENT
                    storage.clear()
                continue

            if self.state == self.START_EVENT:

                if self.item_end(prefix, event, value, storage):
                    self.add(event_filter, event_filter_args, **storage)
                    self.state = self.SEARCHING
                    continue
                try:
                    if self.item_acquire(prefix, event, value, storage, start, end):
                        continue
                    else:
                        self.state = self.SEARCHING
                except DateEndError:
                    break
