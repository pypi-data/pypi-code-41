import os
import pprint

import pytest


def optional_pprint(object_):
    if isinstance(object_, str):
        return object_
    else:
        return pprint.pformat(object_, width=110, compact=True)


def pytest_assertrepr_compare(op, left, right):
    """TDD speedup tool. No more temporary pprint.

    Just copy new value and make it a new reference (we all know you do it)
    Works assuming the order is: 'assert result == reference`, i.e. left is current result and right is a reference.
    """

    if op == "==" and left != right:
        print(f"""
*** (left side of an assertion {type(left)!r}):
{optional_pprint(left)}
---
--- does not match currently defined reference:
--- (right {type(right)!r}):
{optional_pprint(right)}***

""")


@pytest.fixture
def local_test_file():
    this_dir = os.path.dirname(os.path.abspath(__file__))

    def get_path(*file_name):
        target = os.path.join(this_dir, *file_name)
        if not os.path.isfile(target):
            pytest.fail(f"Not existing file: {target}.")
        return target

    return get_path


@pytest.fixture
def local_test_file_content(local_test_file):
    def get_content_from_path(*file_name):
        given_file_path = local_test_file(*file_name)
        if os.path.exists(given_file_path):
            with open(given_file_path, 'r', encoding='utf-8') as f:
                return f.read()

    return get_content_from_path
