from functools import partial
from ..utils import load


__all__ = ["syncs"]


syncs = partial(load, pkg="backup_utils.syncs", suffix="Sync")
