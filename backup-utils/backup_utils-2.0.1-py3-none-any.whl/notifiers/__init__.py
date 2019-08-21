from functools import partial
from ..utils import load


__all__ = ["notifiers"]


notifiers = partial(load, pkg="backup_utils.notifiers", suffix="Notifier")
