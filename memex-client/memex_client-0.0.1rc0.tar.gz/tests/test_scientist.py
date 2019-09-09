#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_brainiac
----------------------------------

tests for `brainiac` module.
"""

import unittest
import dill
import subprocess
from brainiac.scientist import to_correct_type, convert_rows_to_array
from brainiac.protos.brainiac_pb2 import Row


class TestScientist(unittest.TestCase):
    def get_model_bytes(self):
        script = "tests/generate_model_pickle.py"
        ret = subprocess.run(["python", script], stdout=subprocess.PIPE)
        return eval(ret.stdout)

    def test_to_correct_type(self):
        s = "alkjakg"
        f = "92"

        assert to_correct_type(s) == s
        assert to_correct_type(f) == 92.0

    def test_convert_rows_to_array(self):

        d = [Row(points=["1", "2"]), Row(points=["3", "asdf"])]
        assert convert_rows_to_array(d) == [[1.0, 2.0], [3.0, "asdf"]]

    def test_package(self):
        model_bytes = self.get_model_bytes()
        model = dill.loads(model_bytes)
        model.train(1)
        assert model.predict() == [11]
        assert model.score() == [1]
        assert model.temp.get_wow_number() == 11
