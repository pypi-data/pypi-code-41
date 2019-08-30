# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

import io
import os

import yaml

from polarion_docstrings import checker

CONFIG_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "polarion_tools.yaml.template"
)

EXPECTED = [
    (7, 4, 'P666 Unknown field "foo"'),
    (20, 8, 'P667 Invalid value "huge" of the "caseimportance" field'),
    (21, 8, 'P666 Unknown field "bar"'),
    (
        22,
        8,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (23, 12, "P663 Wrong indentation, line ignored"),
    (31, 4, 'P669 Missing required field "initialEstimate"'),
    (35, 8, 'P669 Missing required field "initialEstimate"'),
    (41, 8, 'P669 Missing required field "initialEstimate"'),
    (44, 12, 'P666 Unknown field "baz"'),
    (51, 0, 'P669 Missing required field "initialEstimate"'),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file_merge):
    with io.open(CONFIG_TEMPLATE, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    errors = checker.DocstringsChecker(None, source_file_merge, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert errors == EXPECTED
