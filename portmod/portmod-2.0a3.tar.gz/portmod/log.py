# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from portmod.colour import colour
from colorama import Fore


def warn(string):
    print("{}: {}".format(colour(Fore.YELLOW, "WARNING"), string))


def err(string):
    print("{}: {}".format(colour(Fore.RED, "ERROR"), string))
