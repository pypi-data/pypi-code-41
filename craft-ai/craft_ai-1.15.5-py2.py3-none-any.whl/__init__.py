"""craft ai API python 2/3 client"""

__title__ = "craft-ai"
__version__ = "1.15.5"
__author__ = "craft ai"
__license__ = "BSD-3-Clause"
__copyright__ = "Copyright (c) 2016, craft ai"


from . import errors
from .client import CraftAIClient as Client
from .interpreter import Interpreter
from .time import Time
from .formatters import format_property, format_decision_rules
from .reducer import reduce_decision_rules

# Defining what will be imported when doing `from craftai import *`

__all__ = [
  "Client",
  "errors",
  "Interpreter",
  "Time"
]
