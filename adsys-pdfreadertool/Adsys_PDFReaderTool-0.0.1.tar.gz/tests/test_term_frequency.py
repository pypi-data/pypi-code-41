#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `term_frequency` package."""


import unittest
from click.testing import CliRunner

from term_frequency import term_frequency
from term_frequency import cli


class TestTerm_frequency(unittest.TestCase):
    """Tests for `term_frequency` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'term_frequency.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
