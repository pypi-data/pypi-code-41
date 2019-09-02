"""Base class for MailComposer objects."""

import os
import textwrap

from .exceptions import MailComposerError


class BaseMailComposer(object):
    """Base class for MailComposer objects.

    Your subclass should implement the display() method to open the
    message in its corresponding external application.
    """

    __slots__ = ["_to", "_cc", "_bcc", "_subject",
                 "_body", "_body_format", "_attachments"]

    def __init__(self, **kw):
        """Return a new MailComposer object."""

        if "to" in kw and kw["to"]:
            self._to = self._parse_recipients(kw["to"])
        else:
            self._to = []

        if "cc" in kw and kw["cc"]:
            self._cc = self._parse_recipients(kw["cc"])
        else:
            self._cc = []

        if "bcc" in kw and kw["bcc"]:
            self._bcc = self._parse_recipients(kw["bcc"])
        else:
            self._bcc = []

        if "subject" in kw and kw["subject"]:
            self._subject = str(kw["subject"])
        else:
            self._subject = ""

        if "body" in kw and kw["body"]:
            self._body = str(kw["body"])
        else:
            self._body = ""

        # Note: self._parse_body_format() will check the formatting
        # for this argument and raise an exception if there's a problem.
        if "body_format" in kw:
            self._body_format = self._parse_body_format(kw["body_format"])
        else:
            self._body_format = "hybrid"

        # Attachments are not accepted as a keyword argument
        self._attachments = []

    def __str__(self):
        """Return the message as a string.

        The format approximates RFC 2822.
        """

        headers = []
        lines = []

        # Process the message headers
        if self._to:
            headers.append("To: {0}".format(", ".join(self._to)))
        if self._cc:
            headers.append("CC: {0}".format(", ".join(self._cc)))
        if self._bcc:
            headers.append("BCC: {0}".format(", ".join(self._bcc)))
        if self._subject:
            headers.append("Subject: {0}".format(self._subject))

        # Format the message headers
        for header in headers:
            for line in textwrap.wrap(header, width=78,
                                      subsequent_indent=" "):
                lines.append(line)

        # Add a blank line separating the headers from the body text
        lines.append("")

        # Format the body text
        for body_line in self._body.splitlines():
            if body_line:
                for line in textwrap.wrap(body_line, width=78):
                    lines.append(line)
            else:
                # This is necessary to keep empty lines in the body text
                lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------------

    def attach_file(self, path):
        """Attach the specified file to this message."""

        if os.path.exists(path):
            # Always give the file's absolute path, since the email
            # application might not share our working directory
            self._attachments.append(os.path.abspath(path))

        else:
            message = "No such file or directory: '{0}'".format(path)
            raise MailComposerError(message)

    def display(self, blocking=True):
        """Display this message in your email application."""

        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _parse_body_format(self, body_format):
        """Parse the "body_format" property."""

        if body_format in ("text", "html", "hybrid"):
            return body_format

        else:
            message = "body_format must be one of 'text', 'html', or 'hybrid'"
            raise ValueError(message)

    def _parse_recipients(self, recipients):
        """Parse the "to", "cc", or "bcc" property."""

        if isinstance(recipients, str):
            return [recipients]

        else:
            return list(recipients)

    # ------------------------------------------------------------------------

    @property
    def to(self):
        """List of recipients in the "To:" field."""
        return self._to

    @to.setter
    def to(self, value):
        if value:
            self._to = self._parse_recipients(value)
        else:
            self._to = []

    @to.deleter
    def to(self):
        del self._to
        self._to = []

    # ------------------------------------------------------------------------

    @property
    def cc(self):
        """List of recipients in the "CC:" field."""
        return self._cc

    @cc.setter
    def cc(self, value):
        if value:
            self._cc = self._parse_recipients(value)
        else:
            self._cc = []

    @cc.deleter
    def cc(self):
        del self._cc
        self._cc = []

    # ------------------------------------------------------------------------

    @property
    def bcc(self):
        """List of recipients in the "BCC:" field."""
        return self._bcc

    @bcc.setter
    def bcc(self, value):
        if value:
            self._bcc = self._parse_recipients(value)
        else:
            self._bcc = []

    @bcc.deleter
    def bcc(self):
        del self._bcc
        self._to = []

    # ------------------------------------------------------------------------

    @property
    def subject(self):
        """The subject line of the email."""
        return self._subject

    @subject.setter
    def subject(self, value):
        if value:
            self._subject = str(value)
        else:
            self._subject = ""

    @subject.deleter
    def subject(self):
        del self._subject
        self._subject = ""

    # ------------------------------------------------------------------------

    @property
    def body(self):
        """The body of the email."""
        return self._body

    @body.setter
    def body(self, value):
        if value:
            self._body = str(value)
        else:
            self._body = ""

    @body.deleter
    def body(self):
        del self._body
        self._body = ""

    # ------------------------------------------------------------------------

    @property
    def body_format(self):
        """The format of the message body.

        Possible values are:

          'text'
            Indicates the message body is in plain-text format.

          'html'
            Indicates the message body is in HTML format.

          'hybrid' (default)
            Indicates the message body is in plain-text format, but
            the message should be sent using HTML formatting if your
            email application supports it.
        """
        return self._body_format

    @body_format.setter
    def body_format(self, value):
        self._body_format = self._parse_body_format(value)

    # ------------------------------------------------------------------------

    @property
    def attachments(self):
        """List of files to attach to this email."""
        return self._attachments
