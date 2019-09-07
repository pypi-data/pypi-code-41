"""API for composing emails through an external application.

mailcomposer aims to provide a simple, cross-platform interface for
composing emails through an external application like Microsoft Outlook.

The recommended way to use mailcomposer is via the MailComposer factory
function, which attempts to automatically select the most suitable email
application interface for your system.

Supported interfaces are:

  OutlookComposer
    MAPI-based interface for Microsoft Outlook. Requires the pywin32
    package. This interface is only available on Microsoft Windows.

  ThunderbirdComposer
    Interface for Mozilla Thunderbird.

  XDGEmailComposer
    Fallback interface for Unix using xdg-email.

For testing purposes, there is also a DummyMailComposer interface that
simply prints the message to stdout. It is never selected automatically;
you must explicitly create a DummyMailComposer object to use it.

All email application interfaces are descended from a common base class,
BaseMailComposer, and have identical public attributes and methods.

mailcomposer provides its own exception class, MailComposerError, for
problems that occur during processing. It can, and probably will, also
raise any of the standard Python exceptions if you attempt something
you really shouldn't.
"""

from .base import BaseMailComposer
from .dummy import DummyMailComposer

# Email application interfaces with no special import requirements
from .thunderbird import ThunderbirdComposer
from .xdg_email import XDGEmailComposer

# The Outlook interface will fail to import on non-Windows systems,
# or if pywin32 is not installed
try: from .outlook import OutlookComposer
except (ImportError): OutlookComposer = None

from .exceptions import MailComposerError


def MailComposer(**kw):
    """Email application interface.

    This is a factory function that attempts to automatically select
    the most suitable email application interface for your system.

    A MailComposerError is raised if no supported email application
    can be found.
    """

    # Start with dedicated email clients
    if ThunderbirdComposer:
        return ThunderbirdComposer(**kw)

    # Outlook gets low priority if other email clients are installed.
    # Because Outlook is part of the default Microsoft Office installation,
    # it's more likely than a standalone client to be present but not used.
    elif OutlookComposer:
        return OutlookComposer(**kw)

    # Use xdg-email, which attempts to provide a standard command-line
    # interface on Unix systems, as a last resort.
    elif XDGEmailComposer:
        return XDGEmailComposer(**kw)

    # Raise an exception if no suitable email clients are installed
    else:
        message = "No suitable email clients were found on your system."
        raise MailComposerError(message)


__all__ = [
    "MailComposer",
    "BaseMailComposer",
    "DummyMailComposer",

    # Email application interfaces
    "OutlookComposer",
    "ThunderbirdComposer",

    # Exception classes
    "MailComposerError",
]
