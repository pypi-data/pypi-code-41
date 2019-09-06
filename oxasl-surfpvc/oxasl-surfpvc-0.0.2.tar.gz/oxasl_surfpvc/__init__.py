"""
OXASL plugin for surface based partial volume correction

This module is designed to operate within the OXASL pipeline.
If installed, then it will be called by ``oxasl.oxford_asl.oxasl``
whenever surface based PVC is requested.
"""
from .api import prepare_surf_pvs
from ._version import __version__

__all__ = ["__version__", "prepare_surf_pvs"]
