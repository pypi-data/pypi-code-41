#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

from ebr_trackerbot import cli


def test_cli():
    """Test the CLI."""

    parser = cli.parse_args(
        ["--config", "test_config.yaml", "--vault_config", "test_vault.yaml", "--vault_creds", "test_vault_cred.yaml"]
    )
    assert parser.config == "test_config.yaml"
    assert parser.vault_config == "test_vault.yaml"
    assert parser.vault_creds == "test_vault_cred.yaml"
