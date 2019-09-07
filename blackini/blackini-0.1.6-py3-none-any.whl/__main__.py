#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Monkeypatch black to allow reding config from '.ini` files."""

import configparser
import re
import sys

import toml

from black import main as main_black


def patched_load(*a, **kw):
    """Attempt to read configuration from .ini, if it makes sense."""
    try:
        from pathlib import Path

        file_ = a[0]
        if Path(file_).suffix == ".ini":
            config = configparser.ConfigParser()
            config.read(file_)
            return {
                "tool": {
                    "black": {
                        k: v
                        if "," not in v
                        else [p for p in v.split(",") if p]
                        for k, v in config["tool.black"].items()
                    }
                }
            }
    except BaseException:  # pylint: disable=W0703
        pass
    return toml.decoder.load(*a, **kw)


def main():
    """Monkey-patch `toml.load` before calling black."""
    sys.argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sys.argv[0])

    toml.load = patched_load
    # pylint: disable=E1120
    sys.exit(main_black())


if __name__ == "__main__":
    main()
