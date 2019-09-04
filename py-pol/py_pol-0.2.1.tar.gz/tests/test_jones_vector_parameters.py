# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Jones_vector module"""

import sys

import numpy as np

from py_pol import degrees, eps
from py_pol.jones_vector import Jones_vector
from py_pol.utils import comparison, params_to_list


# TODO: quitar los números pequeños y radianes, etc
class TestJonesVectorParameters(object):
    def test_linear_light(self):

        solution = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution,
            eps), sys._getframe().f_code.co_name + ".py --> example: 0 degrees"

        solution = [
            1.0, 0.7853981633974483, 0.0, 0.7853981633974482, 0.0, 1.0, 0.0
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=45 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution, eps
        ), sys._getframe().f_code.co_name + ".py --> example: 45 degrees"

        solution = [
            1.0, 1.5707963267948966, 0.0, 1.5707963267948966, 0.0, 1.0, 0.0
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=90 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution, eps
        ), sys._getframe().f_code.co_name + ".py --> example: 90 degrees"

        solution1 = [
            1.0, 0.7853981633974484, 0, 0.7853981633974484,
            6.123233995736766e-17, 0.0, 1.0
        ]
        solution2 = [
            1.0, 0.7853981633974484, np.pi, 0.7853981633974484,
            6.123233995736766e-17, 0.0, 1.0
        ]
        solution = np.array(solution2)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=135 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution, eps
        ), sys._getframe().f_code.co_name + ".py --> example: 135 degrees"
        # TODO: delay está mal
        solution = [1.0, 0.0, np.pi, 0.0, 0.0, 1.0, 0.0]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=180 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution, eps
        ), sys._getframe().f_code.co_name + ".py --> example: 180 degrees"

    def test_circular_light(self):

        solution = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert comparison(
            proposal, solution,
            eps), sys._getframe().f_code.co_name + ".py --> example: 0 degrees"
