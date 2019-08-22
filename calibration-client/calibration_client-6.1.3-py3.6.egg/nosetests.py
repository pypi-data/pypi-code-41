"""Nosetests Configuration File"""
# ! /usr/bin/python

import os

from nose import main

if __name__ == "__main__":
    os.chdir("tests")
    main()
    os.chdir("..")
