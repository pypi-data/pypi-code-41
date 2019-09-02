"""
    This is a our invoke program
"""
import os
import sys
import logging
from invoke import Program, Collection
from .sidney import sidney
from . import create
from . import run
from . import stop

VERSION = "0.2.6"

sys.path.insert(0, os.getcwd())

logging.basicConfig(level=logging.INFO)

_NAMESPACE_ = Collection()
try:
    import bluemax.sa.tasks

    _NAMESPACE_.add_collection(Collection.from_module(bluemax.sa.tasks), name="db")
except ImportError:
    pass

_NAMESPACE_.add_task(sidney)
_NAMESPACE_.add_collection(Collection.from_module(create))
_NAMESPACE_.add_collection(Collection.from_module(run))
_NAMESPACE_.add_task(stop.stop)

program = Program(
    version=VERSION, namespace=_NAMESPACE_
)  # pylint: disable=C0103
