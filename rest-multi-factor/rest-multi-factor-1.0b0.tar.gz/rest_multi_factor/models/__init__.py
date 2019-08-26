"""
Model package.

Here is the backbone of the REST multi factor package defined.
The models are responsible for generating, storing and validating
one time passwords and pre-shared secrets.
"""

__all__ = (
    "Device",
    "Challenge"
)

from rest_multi_factor.models.base import Challenge, Device
