from functools import partial
from ..utils import load


__all__ = ["tasks"]


tasks = partial(load, pkg="backup_utils.tasks", suffix="Task")
