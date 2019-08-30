"""Custom MySQL Component Executor"""

from typing import Any, Dict, List, NamedTuple, Text

import tensorflow as tf
from tfx import types
from tfx.components.base import base_executor
from tfx.types import artifact_utils