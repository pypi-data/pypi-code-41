#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fixtures for testing the 'seamm_ff_util' package."""

import pytest
from seamm_ff_util import Forcefield
from seamm_ff_util import FFAssigner


@pytest.fixture(scope='session')
def pcff():
    """A forcefield object initialized with PCFF
    """
    pcff = Forcefield('data/pcff2018.frc')
    pcff.initialize_biosym_forcefield()
    return pcff


@pytest.fixture(scope='session')
def pcff_assigner(pcff):
    """A forcefield object initialized with PCFF
    """
    pcff_assigner = FFAssigner(pcff)
    return pcff_assigner
