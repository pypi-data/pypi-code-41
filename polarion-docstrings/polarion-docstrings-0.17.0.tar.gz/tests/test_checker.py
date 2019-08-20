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
    (10, 4, 'P669 Missing required field "assignee"'),
    (10, 4, 'P669 Missing required field "initialEstimate"'),
    (14, 8, 'P669 Missing required field "assignee"'),
    (14, 8, 'P669 Missing required field "initialEstimate"'),
    (20, 8, 'P669 Missing required field "initialEstimate"'),
    (22, 12, 'P667 Invalid value "nonexistent" of the "casecomponent" field'),
    (43, 12, 'P667 Invalid value "level1" of the "caselevel" field'),
    (43, 12, 'P668 Field "caselevel" should be handled by the "@pytest.mark.tier" marker'),
    (44, 12, 'P668 Field "caseautomation" should be handled by the "@pytest.mark.manual" marker'),
    (
        45,
        12,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (46, 12, 'P666 Unknown field "foo"'),
    (47, 12, 'P664 Ignoring field "description": use test docstring instead'),
    (54, 0, 'P669 Missing required field "assignee"'),
    (54, 0, 'P669 Missing required field "initialEstimate"'),
    (58, 0, 'P669 Missing required field "assignee"'),
    (58, 0, 'P669 Missing required field "initialEstimate"'),
    (64, 4, 'P669 Missing required field "assignee"'),
    (64, 4, 'P669 Missing required field "initialEstimate"'),
    (75, 8, 'P667 Invalid value "wrong" of the "testSteps" field'),
    (78, 8, 'P667 Invalid value "" of the "expectedResults" field'),
    (93, 4, 'P669 Missing required field "assignee"'),
    (95, 12, "P663 Wrong indentation, line ignored"),
    (100, 4, 'P669 Missing required field "assignee"'),
    (105, 15, "P663 Wrong indentation, line ignored"),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file):
    with io.open(CONFIG_TEMPLATE, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    errors = checker.DocstringsChecker(None, source_file, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert errors == EXPECTED
