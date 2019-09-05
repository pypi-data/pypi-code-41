import unittest

from demo import WordSet


class WordSetTest(unittest.TestCase):
    alphabet = ('a', 'b')
    avoid = frozenset(['aa', 'bb'])
    avoid_subset = frozenset(['bb'])

    def setUp(self):
        self.word_set = WordSet(self.alphabet, self.avoid)
        self.sub_word_set = WordSet(self.alphabet, self.avoid_subset)

    def test_basis(self):
        self.assertEqual(WordSet._basis_of(self.avoid), self.avoid)
        self.assertEqual(WordSet._basis_of({'a', 'aa'}), frozenset({'a'}))

    def test_next_word(self):
        next_word = self.word_set.next_lexicographical_word
        self.assertEqual(next_word(None), '')
        self.assertEqual(next_word(''), 'a')
        self.assertEqual(next_word('a'), 'b')
        self.assertEqual(next_word('b'), 'aa')
        self.assertEqual(next_word('aa'), 'ab')
        self.assertEqual(next_word('ab'), 'ba')
        self.assertEqual(next_word('ba'), 'bb')
        self.assertEqual(next_word('bb'), 'aaa')
        self.assertEqual(next_word('aaa'), 'aab')

    def test_contains_word(self):
        self.assertFalse(self.word_set.contains('aa'))
        self.assertFalse(self.word_set.contains('bb'))
        self.assertFalse(self.word_set.contains('abba'))
        self.assertFalse(self.word_set.contains('bababaa'))

        self.assertTrue(self.word_set.contains(''))
        self.assertTrue(self.word_set.contains('a'))
        self.assertTrue(self.word_set.contains('b'))
        self.assertTrue(self.word_set.contains('ab'))
        self.assertTrue(self.word_set.contains('bababa'))

    def test_words_of_length(self):
        length_five_words = self.word_set.get_elmnts(of_size=5)
        self.assertListEqual(length_five_words, ['ababa', 'babab'])

        length_zero_words = self.word_set.get_elmnts(of_size=0)
        self.assertListEqual(length_zero_words, [''])

        negative_length_words = self.word_set.get_elmnts(of_size=-1)
        self.assertListEqual(negative_length_words, [])

    def test_all_subwords_of_word(self):
        subwords = WordSet._get_all_subwords_of('aba')
        expected_subwords = ['a', 'ab', 'aba', 'b', 'ba']
        self.assertEqual(subwords, expected_subwords)

    def test_avoiding_subsets(self):
        expected_subsets = {frozenset({"aa", "bb"}), frozenset({"aa", "b"}),
                            frozenset({"a", "bb"}), frozenset({'a', 'b'})}
        subsets = self.word_set.get_all_avoiding_subsets()
        self.assertEqual(subsets, expected_subsets)

    def test_equality(self):
        word_set = WordSet(self.alphabet, self.avoid)
        word_set_eq = WordSet(self.alphabet, self.avoid)
        self.assertEqual(word_set, word_set_eq)

    def test_equality_reversed_alphabet(self):
        word_set = WordSet(self.alphabet, self.avoid)
        word_set_rev = WordSet(list(reversed(self.alphabet)), self.avoid)
        self.assertNotEqual(word_set, word_set_rev)

    def test_equality_nonsense(self):
        word_set = WordSet(self.alphabet, self.avoid)
        self.assertNotEqual(word_set, "nonsense")
        self.assertNotEqual(word_set, None)


if __name__ == '__main__':
    unittest.main()
