"""Demonstration of the MailComposer class."""

import os
import argparse

from . import *


DESCRIPTION = """\
Compose an email message through your desktop client.

If at least one recipient is specified, mailcomposer will default to
behaving like the Unix mail(1) utility:

  * If no subject line is specified using the "-s" argument, it will
    prompt for one.

  * It will then treat all further input as the message body, until
    it encounters either a line containing a single "." or end-of-file.

If no recipient is specified, or the "--no-prompt" argument is present,
mailcomposer will open a new message immediately without prompting for
a subject or body, but will still process other command-line arguments.
"""

FORMATTER_CLASS = argparse.RawTextHelpFormatter

try:
    # Python 2
    getline = raw_input
except (NameError):
    # Python 3
    getline = input


def demo():
    """Demonstrate the MailComposer class."""

    parser = argparse.ArgumentParser(prog="mailcomposer",
                                     description=DESCRIPTION,
                                     formatter_class=FORMATTER_CLASS)

    std_args = parser.add_argument_group("standard arguments")
    std_args.add_argument("to_addr",
                          type=str, nargs="*",
                          help="the recipient's email address")
    std_args.add_argument("-c",
                          type=str, action="append",
                          dest="cc", metavar="address",
                          help="send a carbon copy to this address")
    std_args.add_argument("-b",
                          type=str, action="append",
                          dest="bcc", metavar="address",
                          help="send a blind carbon copy to this address")
    std_args.add_argument("-s",
                          type=str, action="store",
                          dest="subject", metavar="subject",
                          help="specify the subject of the message")

    mc_args = parser.add_argument_group("mailcomposer-specific arguments")
    mc_args.add_argument("--no-prompt",
                         action="store_false", dest="prompt",
                         help="don't prompt for a message body")
    mc_args.add_argument("--body-format",
                         type=str, action="store",
                         dest="body_format", metavar="format",
                         choices=["text", "html", "hybrid"], default="hybrid",
                         help="specify the message format (text, html, "
                              "or hybrid)")
    mc_args.add_argument("--attach-file",
                         type=str, action="append",
                         dest="attachments", metavar="path",
                         help="attach the specified file to this message")

    # ------------------------------------------------------------------------

    # Parse command-line arguments
    args = parser.parse_args()

    # Pass arguments to our MailComposer
    mc = MailComposer(to=args.to_addr,
                      cc=args.cc,
                      bcc=args.bcc,
                      subject=args.subject,
                      body_format=args.body_format)

    # Process file attachments
    if args.attachments:
        for path in args.attachments:
            if os.path.isfile(path):
                mc.attach_file(path)

    # Behave like mail(1) if a recipient was specified
    if args.prompt and args.to_addr:
        # Prompt for a subject if none was specified
        if not args.subject:
            mc.subject = getline("Subject: ")

        # Prompt for body lines until "." or end-of-file
        body_lines = []
        while True:
            try:
                line = getline()
                if line == ".":
                    break
                else:
                    body_lines.append(line)
            except (EOFError):
                break
        mc.body = "\n".join(body_lines)

    # Display the message
    mc.display()


if __name__ == "__main__":
    demo()
