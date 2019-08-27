#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `python_helpers` package."""

import pytest

from click.testing import CliRunner

from python_helpers import python_helpers
from python_helpers import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'python_helpers.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


@pytest.mark.parametrize(
    "test_input,desired_output",
    (
        (r'C:\Program Files\My Program', r'"C:\Program Files\My Program"'),
        (r'323523523', r'"323523523"'),
        (r'323523523', r'"323523523"'),
        (r'/usr/bin/path', r'"/usr/bin/path"'),
    )
)
def test_quote_string(test_input, desired_output):
    """Test the quote_string() function"""
    assert desired_output == python_helpers.quote_line(test_input)
