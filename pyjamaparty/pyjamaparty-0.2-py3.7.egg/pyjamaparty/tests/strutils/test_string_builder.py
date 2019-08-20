import unittest
from pyjamaparty.strutils import string_builder as sb


class TestStringBuilder(unittest.TestCase):

    def test_noarg_builder(self):
        s = sb.StringBuilder()
        self.assertTrue(isinstance(s, sb.StringBuilder))
        self.assertEqual(len(s), 0)

    def test_empty_builder(self):
        s = sb.StringBuilder("")
        self.assertTrue(isinstance(s, sb.StringBuilder))
        self.assertEqual(len(s), 0)

    def test_arg_builder(self):
        expected_str = "wow"
        s = sb.StringBuilder(expected_str)
        self.assertTrue(isinstance(s, sb.StringBuilder))
        self.assertEqual(len(s), len(expected_str))
        self.assertEqual(expected_str, str(s))

    def test_append_builder(self):
        expected_str = "wow"
        s = sb.StringBuilder()
        s.append(expected_str)
        self.assertEqual(expected_str, str(s))

    def test_chained_append_builder(self):
        expected_str = "wow"
        s = sb.StringBuilder()
        s.append(expected_str).append(expected_str)
        self.assertEqual('{}{}'.format(expected_str, expected_str), str(s))

    def test_modify_str_builder(self):
        original_str = "wow, such a nice builder"
        modified_str = "whee, such a nice builder"
        s = sb.StringBuilder(original_str)
        s[:3] = "whee"
        self.assertEqual(modified_str, str(s))

    def test_get_substring_builder(self):
        original_str = "wow, such a nice builder"
        s = sb.StringBuilder(original_str)
        sub_str = s[:3]
        self.assertEqual("wow", sub_str)

    def test_convert_to_str_builder(self):
        s = sb.StringBuilder("wow")
        self.assertTrue(isinstance(str(s), str))

    def test_len_str_builder(self):
        original_str = "wow"
        s = sb.StringBuilder(original_str)
        self.assertEqual(len(original_str), len(s))

    def test_iter_str_builder(self):
        original_str = "wow"
        str_builder = sb.StringBuilder(original_str)
        for i, s in enumerate(str_builder):
            self.assertEqual(original_str[i], s)

    def test_concat_str_builder(self):
        original_str = "wow"
        s = sb.StringBuilder(original_str)
        s += original_str
        self.assertEqual('{}{}'.format(original_str, original_str), str(s))

    def test_to_string_builder(self):
        s = sb.StringBuilder("wow")
        self.assertTrue(isinstance(s.to_string(), str))
