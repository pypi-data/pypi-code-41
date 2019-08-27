from functools import reduce
from enum import Enum, Flag, auto


class Event(Flag):
    NONE = 0
    WORKSPACE = auto()
    OUTPUT = auto()
    MODE = auto()
    WINDOW = auto()
    BARCONFIG_UPDATE = auto()
    BINDING = auto()
    SHUTDOWN = auto()
    TICK = auto()

    @classmethod
    def ALL(cls):
        return reduce(lambda x, y: x | y, cls)

    def canonical_names(self):
        return [event.name.lower() for event in Event if self & event]


class EventType(Enum):
    WORKSPACE = 0
    OUTPUT = 1
    MODE = 2
    WINDOW = 3
    BARCONFIG_UPDATE = 4
    BINDING = 5
    SHUTDOWN = 6
    TICK = 7

    @property
    def flag(self):
        return getattr(Event, self.name)


class MessageType(Enum):
    RUN_COMMAND = 0
    GET_WORKSPACES = 1
    SUBSCRIBE = 2
    GET_OUTPUTS = 3
    GET_TREE = 4
    GET_MARKS = 5
    GET_BAR_CONFIG = 6
    GET_VERSION = 7
    GET_BINDING_MODES = 8
    GET_CONFIG = 9
    SEND_TICK = 10
    SYNC = 11
