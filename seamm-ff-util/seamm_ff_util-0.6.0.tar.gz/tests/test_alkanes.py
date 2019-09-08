#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `seamm_ff_util.ff_assigner` package."""


def test_methane(pcff_assigner):
    """Test of atom-type assignment for methane"""
    assert pcff_assigner.assign('C') == ['c', 'hc', 'hc', 'hc', 'hc']


def test_ethane(pcff_assigner):
    """Test of atom-type assignment for ethane"""
    assert pcff_assigner.assign('CC') == [
        'c3', 'c3', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc'
    ]


def test_propane(pcff_assigner):
    """Test of atom-type assignment for propane"""
    assert pcff_assigner.assign('CCC') == [
        'c3', 'c2', 'c3', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc'
    ]


def test_isobutane(pcff_assigner):
    """Test of atom-type assignment for isobutane"""
    assert pcff_assigner.assign('CC(C)C') == [
        'c3', 'c1', 'c3', 'c3', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc',
        'hc', 'hc'
    ]


def test_neopentane(pcff_assigner):
    """Test of atom-type assignment for neopentane"""
    assert pcff_assigner.assign('CC(C)(C)C') == [
        'c3', 'c', 'c3', 'c3', 'c3', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc', 'hc',
        'hc', 'hc', 'hc', 'hc', 'hc'
    ]
