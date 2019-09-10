# pylint: disable=missing-docstring

import os

import yaml

from polarion_docstrings import checker

CONFIG_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "polarion_tools.yaml.template"
)

EXPECTED = [
    (7, 4, 'P669 Missing required field "assignee"'),
    (7, 4, 'P669 Missing required field "initialEstimate"'),
    (11, 8, 'P669 Missing required field "assignee"'),
    (11, 8, 'P669 Missing required field "initialEstimate"'),
    (17, 8, 'P669 Missing required field "initialEstimate"'),
    (19, 12, 'P667 Invalid value "nonexistent" of the "casecomponent" field'),
    (40, 12, 'P667 Invalid value "level1" of the "caselevel" field'),
    (40, 12, 'P668 Field "caselevel" should be handled by the "@pytest.mark.tier" marker'),
    (41, 12, 'P668 Field "caseautomation" should be handled by the "@pytest.mark.manual" marker'),
    (
        42,
        12,
        'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker',
    ),
    (43, 12, 'P666 Unknown field "foo"'),
    (44, 12, 'P664 Ignoring field "description": use test docstring instead'),
    (51, 0, 'P669 Missing required field "assignee"'),
    (51, 0, 'P669 Missing required field "initialEstimate"'),
    (55, 0, 'P669 Missing required field "assignee"'),
    (55, 0, 'P669 Missing required field "initialEstimate"'),
    (61, 4, 'P669 Missing required field "assignee"'),
    (61, 4, 'P669 Missing required field "initialEstimate"'),
    (72, 8, 'P667 Invalid value "wrong" of the "testSteps" field'),
    (75, 8, 'P667 Invalid value "" of the "expectedResults" field'),
    (90, 4, 'P669 Missing required field "assignee"'),
    (92, 12, "P663 Wrong indentation, line ignored"),
    (97, 4, 'P669 Missing required field "assignee"'),
    (102, 15, "P663 Wrong indentation, line ignored"),
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file):
    with open(CONFIG_TEMPLATE, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    errors = checker.DocstringsChecker(None, source_file, config, "TestChecker").run_checks()
    errors = _strip_func(errors)
    assert errors == EXPECTED
