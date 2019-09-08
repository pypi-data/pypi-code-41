#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_nonbond_explicit(pcff):
    """Simple test of known nonbond parameters"""
    expected = {'eps': '0.02000', 'r': '2.9950', 'reference': '1'}

    i = 'h'
    ptype, key, form, parameters = pcff.nonbond_parameters(i)
    assert ptype == "explicit"
    assert key == ('h', )
    assert parameters == expected


def test_nonbond_equivalent(pcff):
    """Simple test of nonbond parameters using equivalencies"""
    expected = {'eps': '0.06400', 'r': '4.0100', 'reference': '1'}

    i = 'c5'
    ptype, key, form, parameters = pcff.nonbond_parameters(i)
    assert ptype == "equivalent"
    assert key == ('cp', )
    assert parameters == expected
