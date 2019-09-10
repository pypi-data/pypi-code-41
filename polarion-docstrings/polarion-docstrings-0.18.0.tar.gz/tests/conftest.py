# pylint: disable=missing-docstring

import os

import pytest

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture(scope="module")
def source_file():
    return os.path.relpath(os.path.join(DATA_PATH, "polarion_docstrings.py"))


@pytest.fixture(scope="module")
def source_file_merge():
    return os.path.relpath(os.path.join(DATA_PATH, "polarion_docstrings_merge.py"))
