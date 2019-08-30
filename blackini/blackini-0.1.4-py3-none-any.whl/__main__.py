#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Monkeypatch black to allow reding config from '.ini` files."""

import configparser
import re
import sys

from black import main as main_black
import toml


def patched_load(*a, **kw):
    try:
        from pathlib import Path

        file_ = a[0]
        if Path(file_).suffix == ".ini":
            config = configparser.ConfigParser()
            config.read(file_)
            return {
                "tool": {
                    "black": {k: v for k, v in config["tool.black"].items()}
                }
            }
    except BaseException:
        pass
    return toml.decoder.load(*a, **kw)

def main():
    sys.argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sys.argv[0])
    
    toml.load = patched_load
    sys.exit(main_black())

if __name__ == "__main__":
    main()
