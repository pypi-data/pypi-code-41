#!/usr/bin/python

# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import sys
import os
from os import path as osp


def main():
    if osp.isfile(
        osp.join(
            osp.dirname(osp.dirname(osp.realpath(__file__))), ".portmod_not_installed"
        )
    ):
        sys.path.insert(0, osp.dirname(osp.dirname(osp.realpath(__file__))))

    # Avoid buffering so that we can read from other processes as they output
    os.environ["PYTHONUNBUFFERED"] = "1"

    from portmod.main import main as portmod_main

    portmod_main()


if __name__ == "__main__":
    main()
