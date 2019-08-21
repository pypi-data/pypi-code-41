__all__ = [
    "register",
    "Config",
    "c",
    "color",
    "Color",
    "echo",
    "exit",
    "ReceptError",
    "version",
    "__version__",
    # Click functions
    "group",
    "pass_context",
    "pass_obj",
    "argument",
    "option",
    "Path",
]


import click

from recept.cli import register
from recept.config import Config
from recept.termui import Color, echo, exit
from recept.errors import ReceptError
from recept.version import version, __version__

c = color = Color


# Click functions

group = click.group
pass_context = click.pass_context
pass_obj = click.pass_obj
argument = click.argument
option = click.option
Path = click.Path
