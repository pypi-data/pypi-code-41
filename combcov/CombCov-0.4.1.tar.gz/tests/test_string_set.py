import unittest

from demo import StringSet


class StringSetTest(unittest.TestCase):
    alphabet = ('a', 'b')
    avoid = frozenset(['aa', 'bb'])
    avoid_subset = frozenset(['bb'])

    def setUp(self):
        self.string_set = StringSet(self.alphabet, self.avoid)
        self.sub_string_set = StringSet(self.alphabet, self.avoid_subset)

    def test_next_string(self):
        next_string = self.string_set.next_lexicographical_string
        self.assertEqual(next_string(None), '')
        self.assertEqual(next_string(''), 'a')
        self.assertEqual(next_string('a'), 'b')
        self.assertEqual(next_string('b'), 'aa')
        self.assertEqual(next_string('aa'), 'ab')
        self.assertEqual(next_string('ab'), 'ba')
        self.assertEqual(next_string('ba'), 'bb')
        self.assertEqual(next_string('bb'), 'aaa')
        self.assertEqual(next_string('aaa'), 'aab')

    def test_contains_string(self):
        self.assertFalse(self.string_set.contains('aa'))
        self.assertFalse(self.string_set.contains('bb'))
        self.assertFalse(self.string_set.contains('abba'))
        self.assertFalse(self.string_set.contains('bababaa'))

        self.assertTrue(self.string_set.contains(''))
        self.assertTrue(self.string_set.contains('a'))
        self.assertTrue(self.string_set.contains('b'))
        self.assertTrue(self.string_set.contains('ab'))
        self.assertTrue(self.string_set.contains('bababa'))

    def test_strings_of_length(self):
        length_five_strings = self.string_set.get_elmnts(of_size=5)
        self.assertListEqual(length_five_strings, ['ababa', 'babab'])

        length_zero_strings = self.string_set.get_elmnts(of_size=0)
        self.assertListEqual(length_zero_strings, [''])

        negative_length_strings = self.string_set.get_elmnts(of_size=-1)
        self.assertListEqual(negative_length_strings, [])

    def test_all_substrings_of_string(self):
        substrings = StringSet._get_all_substrings_of('aba')
        expected_substrings = ['a', 'ab', 'aba', 'b', 'ba']
        self.assertEqual(substrings, expected_substrings)

    def test_avoiding_subsets(self):
        expected_subsets = {frozenset({"aa", "bb"}), frozenset({"aa", "b"}),
                            frozenset({"a", "bb"}), frozenset({'a', 'b'})}
        subsets = self.string_set.get_all_avoiding_subsets()
        self.assertEqual(subsets, expected_subsets)

    def test_equality(self):
        string_set = StringSet(self.alphabet, self.avoid)
        string_set_eq = StringSet(self.alphabet, self.avoid)
        self.assertEqual(string_set, string_set_eq)

    def test_equality_reversed_alphabet(self):
        string_set = StringSet(self.alphabet, self.avoid)
        string_set_rev = StringSet(list(reversed(self.alphabet)), self.avoid)
        self.assertNotEqual(string_set, string_set_rev)

    def test_equality_nonsense(self):
        string_set = StringSet(self.alphabet, self.avoid)
        self.assertNotEqual(string_set, "nonsense")
        self.assertNotEqual(string_set, None)


if __name__ == '__main__':
    unittest.main()
