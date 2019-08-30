# testfile---to test the commands
# importing required in-built module
import pytest
import sys
from head import run as head_run
from tail import run as tail_run
from grep import run as grep_run

""" these functions are called when "py.test test_project.py" is run inside
commands directory in PyShell"""


def test_head_run(capfd):
    head_run(-3, "..\\testfile.txt")
    out, err = capfd.readouterr()
    assert out == "hi,\nwelcome,\nhow are you doing,\n\n"


def test_tail_run(capfd):
    tail_run(-3, "..\\testfile.txt")
    out, err = capfd.readouterr()
    assert out == "how are you doing,\ngood,\nbye\n"


def test_grep_run(capfd):
    grep_run("-n", "a", "..\\testfile.txt")
    out, err = capfd.readouterr()
    assert out == "testfile.txt:3: how are you doing,\n\n"
