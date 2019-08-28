# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
try:
    import __builtin__ as builtins
except ImportError:
    import builtins
import _io
import io
import os

from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.lfi import wrappers
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils import compat

try:
    import pathlib
except ImportError:
    pass


@catches_generic_exception(__name__, "Could not instrument for lfi")
def instrument_file_open():
    if compat.PY2:
        InstrumentationManager.instrument(builtins, "open", wrappers.py2_open_wrapper)
        InstrumentationManager.instrument(builtins, "file", wrappers.py2_file_wrapper)
        InstrumentationManager.instrument(os, "open", wrappers.py2_os_open_wrapper)
        InstrumentationManager.instrument(io, "open", wrappers.py2_io_open_wrapper)
        InstrumentationManager.instrument(_io, "open", wrappers.py2_io_open_wrapper)
    else:
        InstrumentationManager.instrument(builtins, "open", wrappers.py3_open_wrapper)
        InstrumentationManager.instrument(os, "open", wrappers.py3_os_open_wrapper)
        InstrumentationManager.instrument(io, "open", wrappers.py3_io_open_wrapper)
        InstrumentationManager.instrument(_io, "open", wrappers.py3_io_open_wrapper)
        # we must patch `pathlib._NormalAccessor.open` explicitly since it has
        # an old reference to `os.open`, otherwise we might get inconsistent
        # behaviour depending on when `pathlib` is imported
        InstrumentationManager.instrument(
            pathlib._NormalAccessor, "open", wrappers.py3_pathlib_normalaccessor_open_wrapper
        )
