import argparse
import os
from unittest import TestCase, mock

from distribute_config import Config


class TestConfig(TestCase):
    def test_define_int(self):
        Config.clear()
        # int and flat float can be assign as int
        Config.define_int("test_int", 5, "A test for int")
        Config.define_int("test_int_float_valid", 5., "A test for int with a float var")

        # But not float
        with self.assertRaises(ValueError):
            Config.define_int("test_int_float_not_valid", 5.5, "A test for int with a float var")

        # Can't assign twice the same variable
        with self.assertRaises(KeyError):
            Config.define_int("test_int", 5, "A test for int")

        self.assertDictEqual(Config.get_dict(), {'test_int': 5, 'test_int_float_valid': 5})

    def test_define_float(self):
        Config.clear()
        Config.define_float("test", 5, "A test for int")
        Config.define_float("test_f", 5., "A test for int with a float var")
        Config.define_float("test_f2", 5.6, "A test for int with a float var")
        Config.define_float("test_str", "5.6", "A test for int with a float var")

        # But not float
        with self.assertRaises(ValueError):
            Config.define_float("test_int_float_not_valid", "bob", "A test for int with a float var")

        self.assertDictEqual(Config.get_dict(), {'test': 5.0, 'test_f': 5.0, 'test_f2': 5.6, 'test_str': 5.6})

    def test_define_str(self):
        Config.clear()
        Config.define_str("test", 5, "A test for int")
        Config.define_str("test_f", 5., "A test for int with a float var")
        Config.define_str("test_f2", 5.6, "A test for int with a float var")
        Config.define_str("test_str", "5.6", "A test for int with a float var")

        self.assertDictEqual(Config.get_dict(), {'test': "5", 'test_f': "5.0", 'test_f2': "5.6", 'test_str': "5.6"})

    def test_define_bool(self):
        Config.clear()
        Config.define_bool("test", 0, "int")
        Config.define_bool("test2", "false", "str")
        Config.define_bool("test3", "truE", "str")
        self.assertDictEqual(Config.get_dict(), {'test': False, 'test2': False, 'test3': True})

    def test_define_enum(self):
        Config.clear()
        Config.define_enum("test", "a", ["a", "b"], "a or b")
        self.assertDictEqual(Config.get_dict(), {"test": "a"})

    def test_define_list(self):
        Config.clear()
        Config.define_float_list("test_float", [5., 6, "7."], "A test for float")
        Config.define_int_list("test_int_float_valid", [5., 5], "A test for int with a float var")
        Config.define_str_list("str", [], "A test for int with a float var")

        self.assertDictEqual(Config.get_dict(), {'test_float': [5.0, 6.0, 7.0], 'test_int_float_valid': [5, 5], "str": []})

    def test_namespace(self):
        Config.clear()
        Config.define_int("namespace1.test_int", 5, "A test for int")
        with Config.namespace("namespace2"):
            Config.define_int("test_int", 5, "A test for int")
            Config.define_int("subnamespace.test_int", 5, "A test for int")

            with Config.namespace("subnamespace2"):
                Config.define_int("plop", 4, "test of subnamespace")

        # print(Config.get_dict())
        self.assertDictEqual(Config.get_dict(), {'namespace1': {'test_int': 5},
                                                 'namespace2': {'test_int': 5, 'subnamespace': {'test_int': 5}, 'subnamespace2': {'plop': 4}}})

    def test_int(self):
        print(Config.get_dict())

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(v1=2, v2=3, c="conf.yml"))
    def test_load_conf(self, mock_args):
        Config.clear()
        if os.path.exists("conf.yml"):
            os.remove("conf.yml")
        Config.define_int("v1", 1, "var")
        Config.define_int("v2", 2, "var")
        Config.load_conf()
        self.assertEqual(Config.get_var("v1"), 2)
        self.assertEqual(Config.get_var("v2"), 3)

    @mock.patch.dict(os.environ, {"V1": "1", "NM__V2": "2"})
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(c="conf2.yml"))
    def test_load_conf_2(self, mock_args):
        Config.clear()
        Config.define_int("v1", 0, "var")
        Config.define_int("nm.v2", 0, "var")
        Config.load_conf()
        self.assertEqual(Config.get_var("v1"), 1)
        self.assertEqual(Config.get_var("nm.v2"), 2)

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(**{"n1.v1": 2, "n1.v2": 3, "n1.v3": False}, c="conf.yml"))
    def test_load_conf_3(self, mock_args):
        Config.clear()
        with Config.namespace("n1"):
            Config.define_int("v1", 1, "var")
            Config.define_int("v2", 2, "var")
            Config.define_bool("V3", True, "turn me false")
        Config.load_conf(no_conf_file=True)
        self.assertEqual(Config.get_var("n1.v1"), 2)
        self.assertEqual(Config.get_var("n1.v2"), 3)
        self.assertEqual(Config.get_var("n1.v3"), False)

    @mock.patch.dict(os.environ, {"N1__V3": "false"})
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(**{"n1.v1": 2, "n1.v2": 3}, c="conf.yml"))
    def test_load_conf_4(self, mock_args):
        Config.clear()
        with Config.namespace("n1"):
            Config.define_int("v1", 1, "var")
            Config.define_int("v2", 2, "var")
            Config.define_bool("V3", True, "turn me false")
        Config.load_conf(no_conf_file=True)
        self.assertEqual(Config.get_var("n1.v1"), 2)
        self.assertEqual(Config.get_var("n1.v2"), 3)
        self.assertEqual(Config.get_var("n1.v3"), False)


    @mock.patch.dict(os.environ, {"N1__V3": "false"})
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(**{"n1.v1": 2, "n1.v2": 3}, c="conf.yml"))
    def test_load_conf_5(self, mock_args):
        Config.clear()
        if os.path.exists("conf.yml"):
            os.remove("conf.yml")
        with Config.namespace("n1"):
            Config.define_int("v1", 1, "var")
            Config.define_int("v2", 2, "var")
            Config.define_bool("V3", True, "turn me false")
        Config.load_conf()
        self.assertEqual(Config.get_var("n1.v1"), 2)
        self.assertEqual(Config.get_var("n1.v2"), 3)
        self.assertEqual(Config.get_var("n1.v3"), False)

    @mock.patch.dict(os.environ, {"VAR": "false"})
    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(c="conf.yml"))
    def test_load_bool(self, mock_args):
        Config.clear()
        Config.define_bool("VaR", True, "turn me false")
        Config.load_conf(no_conf_file=True)
        self.assertEqual(Config.get_var("VAr"), False)
