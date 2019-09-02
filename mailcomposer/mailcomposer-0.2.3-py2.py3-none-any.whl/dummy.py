"""Dummy MailComposer interface."""

# For Python 2 compatibility
from __future__ import print_function

from .base import BaseMailComposer
from .exceptions import MailComposerError


class DummyMailComposer(BaseMailComposer):
    """Dummy MailComposer interface.

    This class is provided mainly for testing, and as a fallback in case
    no other interfaces are available. Calling display() will print the
    message to stdout.
    """

    __slots__ = []

    def display(self, blocking=True):
        """Print the message to stdout."""

        print(str(self))
