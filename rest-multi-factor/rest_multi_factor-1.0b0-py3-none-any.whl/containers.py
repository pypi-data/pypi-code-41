"""Container objects to maintain data before serialization."""

__all__ = (
    "GeneralDeviceContainer",
    "SpecificDeviceContainer",
)

from collections import namedtuple


GeneralDeviceContainer = namedtuple("GeneralDeviceContainer", (
    "index",
    "verbose_name",
    "dispatchable",
))

SpecificDeviceContainer = namedtuple("SpecificDeviceContainer", (
    "index",
    "confirmed",
    "verbose_name",
    "dispatchable",
))
