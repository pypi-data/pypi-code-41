"""MAPI-based interface for Microsoft Outlook (requires pywin32)."""

import win32com.client
import pywintypes

from .base import BaseMailComposer
from .exceptions import MailComposerError


__all__ = ["OutlookComposer"]


try:
    # Connect to Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")

except (pywintypes.com_error):
    # Outlook is not available on this system
    outlook = None


class _OutlookComposer(BaseMailComposer):
    """MAPI-based interface for Microsoft Outlook."""

    __slots__ = []

    def display(self, blocking=True):
        """Display the message in Microsoft Outlook."""

        # Create a new message
        message = outlook.CreateItem(0)

        # Process the message headers
        if self._to:
            message.To = "; ".join(self._to)
        if self._cc:
            message.CC = "; ".join(self._cc)
        if self._bcc:
            message.BCC = "; ".join(self._bcc)
        if self._subject:
            message.Subject = self._subject

        # Format the message body
        if self._body_format == "html":
            message.HTMLBody = self._body
        else:
            # Note that Outlook effectively uses "hybrid" mode
            # by default for composing plain-text messages
            message.Body = self._body

        # Process message attachments
        for path in self._attachments:
            # Outlook requires an absolute path
            message.Attachments.Add(Source=path)

        # Display the message
        message.Display(blocking)


if outlook:
    OutlookComposer = _OutlookComposer

else:
    OutlookComposer = None
