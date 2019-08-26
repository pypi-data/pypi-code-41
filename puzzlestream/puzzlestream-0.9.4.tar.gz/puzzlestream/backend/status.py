from enum import Enum, auto, unique


@unique
class PSStatus(Enum):

    INCOMPLETE = auto()
    ERROR = auto()
    RUNNING = auto()
    TESTFAILED = auto()
    PAUSED = auto()
    WAITING = auto()
    FINISHED = auto()

    def __str__(self) -> str:
        return {
            "INCOMPLETE": "incomplete",
            "ERROR": "error",
            "RUNNING": "running",
            "TESTFAILED": "test failed",
            "PAUSED": "paused",
            "WAITING": "waiting",
            "FINISHED": "finished"
        }[self.name]
