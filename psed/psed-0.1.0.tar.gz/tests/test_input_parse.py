import glob
import os

import pytest

from psed.psed import Psed


def test_not_exists_no_glob(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda x: False)
    monkeypatch.setattr(glob, "glob", lambda x: [])

    psed = Psed(input="dummy")
    with pytest.raises(SystemExit) as excinfo:
        psed._get_input()

    assert str(excinfo.value) == "The input path doesn't exist: 'dummy'"


def test_exists_with_glob(monkeypatch):
    globs = ["file1", "file2"]
    monkeypatch.setattr(os.path, "exists", lambda x: False)
    monkeypatch.setattr(glob, "glob", lambda x: globs)

    psed = Psed(input="dummy")
    input_list = psed._get_input()
    assert input_list == globs


def test_exists_file(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    monkeypatch.setattr(os.path, "isfile", lambda x: True)

    psed = Psed(input="dummy")
    input_list = psed._get_input()
    assert input_list == ["dummy"]


def test_empty_directory(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    monkeypatch.setattr(os.path, "isfile", lambda x: False)
    monkeypatch.setattr(os, "walk", lambda x: [])

    psed = Psed(input="dummy")
    with pytest.raises(SystemExit) as excinfo:
        psed._get_input()

    assert str(excinfo.value) == "Input directory: 'dummy' contains no files."


def test_non_empty_directory(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda x: True)
    monkeypatch.setattr(os.path, "isfile", lambda x: False)
    monkeypatch.setattr(
        os,
        "walk",
        lambda x: [
            ("dummy", ("bar",), ("baz",)),
            (os.path.join("dummy", "bar"), (), ("spam", "eggs")),
        ],
    )

    psed = Psed(input="dummy")
    input_list = psed._get_input()

    assert input_list == [
        os.path.join("dummy", "baz"),
        os.path.join("dummy", "bar", "spam"),
        os.path.join("dummy", "bar", "eggs"),
    ]
