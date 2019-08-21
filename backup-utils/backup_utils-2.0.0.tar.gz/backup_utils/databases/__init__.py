from functools import partial
from ..utils import load


__all__ = ["databases"]


databases = partial(load, pkg="backup_utils.databases", suffix="Db")
