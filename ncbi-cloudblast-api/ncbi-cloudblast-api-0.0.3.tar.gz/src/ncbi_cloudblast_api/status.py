from enum import unique, Enum


@unique
class Status(Enum):
    """
    The current status of a job
    """
    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2
