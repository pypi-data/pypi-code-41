# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from polarion_docstrings.parser import get_docstrings_in_file, merge_docstrings

EXPECTED = {
    "tests/data/polarion_docstrings_merge.py": {
        "assignee": "mkourim",
        "foo": "this is an unknown field",
    },
    "tests/data/polarion_docstrings_merge.py::TestClassFoo": {
        "assignee": "psegedy",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/polarion_docstrings_merge.py::TestClassFoo::test_in_class_no_docstring": {
        "assignee": "psegedy",
        "foo": "this is an unknown field",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/polarion_docstrings_merge.py::TestClassFoo::test_in_class_no_polarion": {
        "assignee": "psegedy",
        "foo": "this is an unknown field",
        "caseimportance": "huge",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": [
            "1. Step with really long description that doesn't fit into one line",
            "2. Do that",
        ],
    },
    "tests/data/polarion_docstrings_merge.py::TestClassFoo::test_in_class_polarion": {
        "assignee": "mkourim",
        "foo": "this is an unknown field",
        "caseimportance": "low",
        "bar": "this is an unknown field",
        "linkedWorkItems": "FOO, BAR",
        "testSteps": ["1. Do that"],
        "baz": "this is an unknown field",
    },
    "tests/data/polarion_docstrings_merge.py::test_standalone_no_docstring": {
        "assignee": "mkourim",
        "foo": "this is an unknown field",
    },
}


def test_parser_merged(source_file_merge):
    docstrings = get_docstrings_in_file(source_file_merge)
    merged_docstrings = merge_docstrings(docstrings)
    assert merged_docstrings == EXPECTED
