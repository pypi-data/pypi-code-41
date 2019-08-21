import io
import sys
import enum
from typing import Union

import click


class Color(enum.Enum):
    """Available colors in terminal."""

    black = "black"
    red = "red"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    magenta = "magenta"
    cyan = "cyan"
    white = "white"
    bright_black = "bright_black"
    bright_red = "bright_red"
    bright_green = "bright_green"
    bright_yellow = "bright_yellow"
    bright_blue = "bright_blue"
    bright_magenta = "bright_magenta"
    bright_cyan = "bright_cyan"
    bright_white = "bright_white"


def echo(
    message: str = None,
    file: io.TextIOBase = None,
    nl: bool = True,
    err: bool = False,
    fg: Union[str, Color] = None,
    bg: Union[str, Color] = None,
    bold: bool = None,
    dim: bool = None,
    underline: bool = None,
    blink: bool = None,
):
    """Print a message plus a newline to the given file or stdout.

    Supported color names are: black, red, green, yellow, blue, magenta, cyan,
    white, bright_black, bright_red, bright_green, bright_yellow, bright_blue,
    bright_magenta, bright_cyan, bright_white.

    Args:
        message: Message to print.
        file: File to write to (defaults to `stdout`).
        err: if set to `True` the file defaults to `stderr` instead of
            `stdout`.
        nl: if set to `True` (the default) a newline is printed afterwards.
        fg: if provided this will become the message foreground color.
        bg: if provided this will become the message background color.
        bold: if provided this will enable or disable bold mode.
        dim: if provided this will enable or disable dim mode.
        underline: if provided this will enable or disable underline.
        blink: if provided this will enable or disable blinking.
    """

    click.secho(
        message=message,
        file=file,
        nl=nl,
        err=err,
        fg=fg.value if isinstance(fg, Color) else fg,
        bg=bg.value if isinstance(bg, Color) else bg,
        bold=bold,
        dim=dim,
        underline=underline,
        blink=blink,
    )


def exit(status: int = None, message: str = None):
    """Exit the application with optional error message.

    If the status is omitted or None, it defaults to zero (i.e., success).
    If the status is an integer, it will be used as the system exit status.
    If the message is provided it will be printed to stderr.

    Args:
        status: Exit status. None = 0, i.e. success. Every other integer is
            interpreted as failure.
        message: Optional message printed to stderr before exiting the
            application.
    """
    if message is not None:
        echo(message=message, err=True, fg=Color.red)
    sys.exit(0 if status is None else status)
