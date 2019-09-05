import unittest
from unittest.mock import call, patch

from pulp import GUROBI_CMD, PULP_CBC_CMD, LpProblem

import pytest
from combcov import CombCov
from demo.word_set import WordSet


class CombCovTest(unittest.TestCase):

    def setUp(self) -> None:
        alphabet = ('a', 'b')
        avoid = frozenset(['aa'])
        self.word_set = WordSet(alphabet, avoid)
        self.max_elmnt_size = 7

        with patch.object(LpProblem, 'solve', return_value=None):
            self.comb_cov = CombCov(self.word_set, self.max_elmnt_size)
            self.comb_cov.solution = [
                WordSet(('a', 'b'), frozenset(['a', 'b']), ""),
                WordSet(('a', 'b'), frozenset(['a', 'b']), "a"),
                WordSet(('a', 'b'), frozenset(['aa']), "b"),
                WordSet(('a', 'b'), frozenset(['aa']), "ab"),
            ]

    def test_actually_solving_with_CBC(self) -> None:
        old_solution = self.comb_cov.solution.copy()
        with patch.object(GUROBI_CMD, 'available', return_value=False):
            self.comb_cov._solve()  # overwrites comb_cov.solution
        assert frozenset(self.comb_cov.solution) == frozenset(old_solution)

    def test_solution_iteration(self) -> None:
        iter_solution = [rule for rule in self.comb_cov]
        assert frozenset(self.comb_cov.solution) == frozenset(iter_solution)

    def test_print_solution_no_side_effect(self) -> None:
        old_solution = self.comb_cov.solution.copy()
        self.comb_cov.print_outcome()
        assert old_solution == self.comb_cov.solution

    def test_print_solution_sunny(self) -> None:
        with patch('builtins.print') as mocked_print:
            self.comb_cov.print_outcome()
            assert call("Solution found!") in mocked_print.mock_calls
            assert len(mocked_print.mock_calls) == 5

    def test_print_solution_rainy(self) -> None:
        with patch('builtins.print') as mocked_print:
            self.comb_cov.solution = []
            self.comb_cov.print_outcome()
            assert call("No solution found.") in mocked_print.mock_calls
            assert len(mocked_print.mock_calls) == 1

    def test_too_many_subrules(self) -> None:
        subrules = list(self.word_set.get_subrules())
        too_many = subrules + [self.word_set] + subrules

        correct_rules = self.comb_cov.rules
        with patch.object(WordSet, 'get_subrules', return_value=too_many):
            comb_cov = CombCov(self.word_set, self.max_elmnt_size)
            assert frozenset(correct_rules) == frozenset(comb_cov.rules)

    def test_no_solver(self) -> None:
        with patch.object(GUROBI_CMD, 'available', return_value=False):
            with patch.object(PULP_CBC_CMD, 'available', return_value=False):
                with pytest.raises(RuntimeError):
                    self.comb_cov._solve()


class RuleTest(unittest.TestCase):

    def setUp(self) -> None:
        alphabet = ('a', 'b')
        avoid = frozenset(['aa', 'bb'])
        avoid_subset = frozenset(['bb'])
        prefix = "ab"
        self.word_set = WordSet(alphabet, avoid, prefix)
        self.sub_word_set = WordSet(alphabet, avoid_subset, prefix)

    def test_elements(self) -> None:
        word_length = 4
        for elmnt in self.word_set.get_elmnts(of_size=word_length):
            self.assertEqual(word_length, len(elmnt))

        elmnts = []
        for length in range(word_length + 1):
            elmnts.extend(self.word_set.get_elmnts(of_size=length))

        expected_rule_elmnts = frozenset(['ab', 'aba', 'abb', 'abab', 'abba'])
        self.assertEqual(expected_rule_elmnts, frozenset(elmnts))

    def test_rule_generation(self) -> None:
        rules = self.word_set.get_subrules()
        self.assertNotIn(None, rules)


if __name__ == '__main__':
    unittest.main()
