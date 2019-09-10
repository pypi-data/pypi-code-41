"""The ``p10s`` module doesn't contain any actual code, is exists to
provide a convenient way to import code into a p10s script.

Example:

.. code-block:: python

    from p10s import tf, k8s

The following things are importable from this module:

``tf``
    just the ``p10s.terraform`` module
``k8s``
    the ``p10s.kubernetes`` module
``values``
    the ``p10s.values`` module
``yaml``, ``json``, ``hcl``
    parsers for syntax of the given type

"""

from p10s.loads import yaml, json, hcl  # noqa: F401

import p10s.kubernetes as k8s  # noqa: F401
import p10s.terraform as tf  # noqa: F401
import p10s.values  # noqa: F401
from p10s.__version__ import __version__  # noqa: F401

from p10s.generator import register_context
