# coding=utf-8

from enum import Enum
from blinker import signal

class ModeEnum(Enum):
    """Enumerator describing the optimization training strategy."""
    MIN = 0
    MAX = 1

on_epoch_begin = signal("on_epoch_begin")
on_epoch_end = signal("on_epoch_end")
on_batch_begin = signal("on_batch_begin")
on_batch_end = signal("on_batch_end")
on_train_begin = signal("on_train_begin")
on_train_end = signal("on_train_end")
# validation sigs
validate_sig = signal("validate_sig")
on_validate_begin = signal("on_validate_begin")
on_validate_end = signal("on_validate_end")
# session
before_session_initialization = signal("before_session_initialization")