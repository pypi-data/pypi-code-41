# -*- coding: utf-8 -*-

from enum import Enum


class UnitBase(object):

    def __init__(self, description):
        self.id = id
        self.description = description

    def get_id(self):
        return self.id

    def get_description(self):
        return self.description


class Unit(UnitBase, Enum):
    Empty = 'Empty',
    Bytes = 'bytes',
    Kilobytes = 'kilobytes',
    Kibibytes = 'kibibytes',
    Megabits = 'megabits',
    Megabytes = 'megabytes',
    Mebibytes = 'mebibytes',
    Gibibytes = 'gibibytes',
    BitsPerSecond = 'bits per second',
    BytesPerSecond = 'bytes per second',
    KibibytesPerSecond = 'kibibytes per second',
    MegabitsPerSecond = 'megabits per second',
    PerSecond = 'per second',
    Seconds = 'seconds',
    Nanoseconds = 'nanoseconds',
    Microseconds = 'microseconds',
    Milliseconds = 'milliseconds',
    Minutes = 'minutes',
    Hours = 'hours',
    Days = 'days',
    DegreesCelsius = 'degrees Celsius',
    Hertz = 'hertz',
    Megahertz = 'megahertz',
    Fraction = 'fraction',
    Percent = 'percent',
    Cores = 'cores',
    Millicores = 'millicores',
    Microcores = 'microcores',
    Nanocores = 'nanocores'
