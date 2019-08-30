# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from polarion_docstrings.parser import (
    DocstringRecord,
    ErrorRecord,
    ValueRecord,
    get_docstrings_in_file,
)

EXPECTED = {
    "tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_docstring": DocstringRecord(
        lineno=10,
        column=4,
        value={},
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_docstring",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_polarion": DocstringRecord(
        lineno=14,
        column=8,
        value={},
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_no_polarion",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_polarion": DocstringRecord(
        lineno=20,
        column=8,
        value={
            "assignee": ValueRecord(lineno=1, column=12, value="mkourim"),
            "casecomponent": ValueRecord(lineno=2, column=12, value="nonexistent"),
            "caseimportance": ValueRecord(lineno=3, column=12, value="low"),
            "testSteps": [
                ValueRecord(
                    lineno=6,
                    column=16,
                    value="1. Step with really long description that doesn't fit into one line",
                ),
                ValueRecord(lineno=8, column=16, value="2. Do that"),
            ],
            "expectedResults": [
                ValueRecord(
                    lineno=11,
                    column=16,
                    value="1. Success outcome with really long description that doesn't "
                    "fit into one line",
                ),
                ValueRecord(lineno=13, column=16, value="2. second"),
            ],
            "title": ValueRecord(
                lineno=15,
                column=12,
                value="Some test with really long description that doesn't fit into one line",
            ),
            "setup": ValueRecord(
                lineno=18, column=12, value="Do this:\n- first thing\n- second thing"
            ),
            "teardown": ValueRecord(lineno=22, column=12, value="Tear it down"),
            "caselevel": ValueRecord(lineno=23, column=12, value="level1"),
            "caseautomation": ValueRecord(lineno=24, column=12, value="automated"),
            "linkedWorkItems": ValueRecord(lineno=25, column=12, value="FOO, BAR"),
            "foo": ValueRecord(lineno=26, column=12, value="this is an unknown field"),
            "description": ValueRecord(lineno=27, column=12, value="ignored"),
        },
        nodeid="tests/data/polarion_docstrings.py::TestClassFoo::test_in_class_polarion",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_annotated_no_docstring": DocstringRecord(
        lineno=54,
        column=0,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_annotated_no_docstring",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_standalone_no_docstring": DocstringRecord(
        lineno=58,
        column=0,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_standalone_no_docstring",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_annotated_no_polarion": DocstringRecord(
        lineno=64,
        column=4,
        value={},
        nodeid="tests/data/polarion_docstrings.py::test_annotated_no_polarion",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_annotated_polarion": DocstringRecord(
        lineno=72,
        column=4,
        value={
            "assignee": ValueRecord(lineno=1, column=8, value="mkourim"),
            "initialEstimate": ValueRecord(lineno=2, column=8, value="1/4"),
            "testSteps": ValueRecord(lineno=3, column=8, value="wrong"),
            "expectedResults": ValueRecord(lineno=6, column=8, value=""),
        },
        nodeid="tests/data/polarion_docstrings.py::test_annotated_polarion",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_blacklisted": DocstringRecord(
        lineno=85,
        column=4,
        value={"initialEstimate": ValueRecord(lineno=1, column=8, value="1/4")},
        nodeid="tests/data/polarion_docstrings.py::test_blacklisted",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_blacklisted_and_whitelisted": DocstringRecord(
        lineno=93,
        column=4,
        value={
            "initialEstimate": ValueRecord(lineno=1, column=8, value="1/4"),
            "_errors_parsing": [
                ErrorRecord(
                    lineno=2, column=12, type="indent", message="Wrong indentation, line ignored"
                )
            ],
        },
        nodeid="tests/data/polarion_docstrings.py::test_blacklisted_and_whitelisted",
        level="function",
    ),
    "tests/data/polarion_docstrings.py::test_wrong_steps_indent": DocstringRecord(
        lineno=100,
        column=4,
        value={
            "initialEstimate": ValueRecord(lineno=1, column=8, value="1/4"),
            "testSteps": [
                ValueRecord(
                    lineno=3,
                    column=12,
                    value="1. Step with really long description that doesn't fit into one line",
                )
            ],
            "_errors_parsing": [
                ErrorRecord(
                    lineno=5, column=15, type="indent", message="Wrong indentation, line ignored"
                )
            ],
        },
        nodeid="tests/data/polarion_docstrings.py::test_wrong_steps_indent",
        level="function",
    ),
}


def test_parser(source_file):
    docstrings = get_docstrings_in_file(source_file)
    assert docstrings == EXPECTED
