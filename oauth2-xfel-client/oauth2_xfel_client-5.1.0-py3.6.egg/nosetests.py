#! /usr/bin/python
import os

from nose import main

__author__ = 'Luis Maia <luis.maia@xfel.eu>'

if __name__ == "__main__":
    os.chdir("tests")
    main()
    os.chdir("..")
