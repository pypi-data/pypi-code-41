#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `custom_step` package."""

import custom_step


def test_construction():
    """Simplest test that we can make a Custom object"""
    instance = custom_step.Custom()
    assert str(type(instance)) == "<class 'custom_step.custom.Custom'>"
