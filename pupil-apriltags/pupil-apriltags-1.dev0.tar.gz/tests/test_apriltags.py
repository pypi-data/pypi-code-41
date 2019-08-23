#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `apriltags` package."""

import pytest


import pupil_apriltags


@pytest.fixture
def detector():
    return pupil_apriltags.Detector()


def test_detector_init(detector):
    print(detector)
