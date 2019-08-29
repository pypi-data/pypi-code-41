from .utils import DateTimeEncoder
import datetime
import geopy
from geopy import distance
import json
from typing import List


class Event(object):
    """
    Event

    Interface definition for a timeline occurrence

    """

    def __init__(
        self,
        date: datetime.datetime,
        latitude: float,
        longitude: float,
        altitude: float = 0,
    ) -> "Event":
        super(Event, self).__init__()

        self.date = date
        self._lla = geopy.point.Point(latitude, longitude, altitude)
        self._distance = None

    @property
    def latitude(self) -> float:
        """ Provides the latitude in decimal format """
        return self._lla.latitude

    @property
    def longitude(self) -> float:
        """ Provides the longitude in decimal format """
        return self._lla.longitude

    @property
    def altitude(self) -> float:
        """ Provides the altitude in meters """
        return self._lla.altitude

    @property
    def lla(self) -> List[float]:
        """ Provides an array of latitude longitude and altitude """
        return [self._lla.latitude, self._lla.longitude, self._lla.altitude]

    @property
    def distance(self) -> float:
        if self._distance:
            return self._distance.meters

    def distance_3d(self, latitude: float, longitude: float, altitude: float) -> float:
        """ Computes the distance to a reference point given by the input lla """

        _reference_point = [latitude, longitude, altitude]
        self._distance = distance.geodesic(self.lla, _reference_point)
        return self.distance

    def distance_2d(
        self, latitude: float, longitude: float, altitude: float = None
    ) -> float:
        """ Computes the distance to a reference point given by the input lla """

        _reference_point = [latitude, longitude]
        self._distance = distance.geodesic(
            [self._lla.latitude, self._lla.longitude], _reference_point
        )
        return self.distance

    def __len__(self) -> int:
        return 1

    def __str__(self) -> str:
        """String representation of object"""
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
