import unittest
from itertools import product
from math import factorial

from permuta import Av, MeshPatt, Perm, PermSet

import pytest
from combcov import Rule
from demo.mesh_tiling import Cell, MeshTiling, MockAvCoPatts


class MockContainingPattsTest(unittest.TestCase):

    def test_mock_co_patt_nonsense(self):
        with pytest.raises(ValueError):
            MockAvCoPatts({}, [None])

    def test_containing_12(self):
        containing = Perm((0, 1))
        mcc = MockAvCoPatts({}, containing)
        for l in range(5):
            assert len(list(mcc.of_length(l))) == factorial(l) - 1

    def test_avoiding_and_containing_patterns(self):
        avoiding = {Perm((0, 2, 1)), Perm((2, 0, 1))}
        containing = {Perm((0, 1))}
        macp = MockAvCoPatts(avoiding, containing)
        for l in range(5):
            assert len(list(macp.of_length(l))) == (2 ** max(0, l - 1)) - 1


class CellTest(unittest.TestCase):

    def setUp(self):
        self.mp_31c2 = MeshPatt(Perm((2, 0, 1)),
                                ((2, 0), (2, 1), (2, 2), (2, 3)))
        self.mp_cell = Cell(frozenset({self.mp_31c2}), frozenset())
        self.mixed_av_co_cell = Cell(
            frozenset({Perm((0, 2, 1)), Perm((2, 0, 1))}),
            frozenset({Perm((0, 1))})
        )

    def test_empty_cell(self):
        assert (MeshTiling.empty_cell.is_empty())
        assert (not MeshTiling.point_cell.is_empty())
        assert (not MeshTiling.anything_cell.is_empty())

    def test_point_cell(self):
        assert (not MeshTiling.empty_cell.is_point())
        assert (MeshTiling.point_cell.is_point())
        assert (not MeshTiling.anything_cell.is_point())

    def test_anything_cell(self):
        assert (not MeshTiling.empty_cell.is_anything())
        assert (not MeshTiling.point_cell.is_anything())
        assert (MeshTiling.anything_cell.is_anything())

    def test_repr(self):
        assert repr(MeshTiling.empty_cell) == " "
        assert repr(MeshTiling.point_cell) == "o"
        assert repr(MeshTiling.anything_cell) == "S"
        assert repr(self.mp_cell) == "Av({})".format(repr(self.mp_31c2))
        assert repr(self.mp_cell.flip()) == "Co({})".format(repr(self.mp_31c2))
        av_co_cell = Cell(frozenset({self.mp_31c2}), frozenset({self.mp_31c2}))
        assert repr(av_co_cell) == "Av({}) and Co({})".format(
            repr(self.mp_31c2), repr(self.mp_31c2))

    def test_flip(self):
        flipped_cell = Cell(frozenset(), frozenset({self.mp_31c2}))
        assert flipped_cell == self.mp_cell.flip()
        assert self.mp_cell == self.mp_cell.flip().flip()

    def test_get_permclass(self):
        for size in range(1, 5):
            expected_from_empty_cell = set()
            permclass_empty_cell = MeshTiling.empty_cell.get_permclass()
            assert isinstance(permclass_empty_cell, Av)
            assert set(permclass_empty_cell.of_length(
                size)) == expected_from_empty_cell

            expected_from_point_cell = {Perm((0,))} if size == 1 else set()
            permclass_point_cell = MeshTiling.point_cell.get_permclass()
            assert isinstance(permclass_point_cell, PermSet)
            assert set(permclass_point_cell.of_length(
                size)) == expected_from_point_cell

            expected_from_anything_cell = set(PermSet(size))
            permclass_anything_cell = MeshTiling.anything_cell.get_permclass()
            assert isinstance(permclass_anything_cell, PermSet)
            assert set(permclass_anything_cell.of_length(
                size)) == expected_from_anything_cell

        assert isinstance(self.mp_cell.get_permclass(), Av)
        assert isinstance(self.mixed_av_co_cell.get_permclass(), MockAvCoPatts)


class PermTest(unittest.TestCase):

    def setUp(self) -> None:
        self.p = Perm((1, 0))
        self.mt = MeshTiling({(0, 0): Cell(frozenset({self.p}), frozenset())})

    def test_that_obstructions_are_perms(self) -> None:
        for subrule in self.mt.get_subrules():
            for obstructions in subrule.get_obstructions_lists():
                for obstruction in obstructions:
                    assert isinstance(obstruction, Perm)


class MeshTilingTest(unittest.TestCase):

    def setUp(self):
        self.p_312 = Perm((2, 0, 1))
        self.mp_31c2 = MeshPatt(self.p_312, ((2, 0), (2, 1), (2, 2), (2, 3)))
        self.mp_1c2 = self.mp_31c2.sub_mesh_pattern([1, 2])

        self.root_mp_cell = Cell(frozenset({self.mp_31c2}), frozenset())
        self.sub_mp_cell = Cell(frozenset({self.mp_1c2}), frozenset())

        self.empty_mt = MeshTiling()
        self.any_mt = MeshTiling({(0, 0): MeshTiling.anything_cell})
        self.root_mt = MeshTiling({
            (0, 0): self.root_mp_cell,
        })
        self.sub_mt = MeshTiling({
            (0, 0): self.root_mp_cell,
            (1, 1): MeshTiling.point_cell,
            (2, 0): self.sub_mp_cell,
        })

    def test_is_instance_of_Rule(self):
        assert isinstance(self.sub_mt, Rule)
        assert isinstance(self.root_mt, Rule)
        assert isinstance(self.empty_mt, Rule)

    def test_padding_removal(self):
        padded_sub_mt = MeshTiling({
            (1, 1): self.root_mp_cell,
            (2, 2): MeshTiling.point_cell,
            (3, 1): self.sub_mp_cell,
        })
        assert padded_sub_mt == self.sub_mt

    def test_any_mt(self):
        any_tiling = self.any_mt.tiling
        assert len(any_tiling) == 1
        assert any_tiling[0] == MeshTiling.anything_cell

    def test_number_to_coordinates_conversions(self):
        assert self.sub_mt.convert_linear_number_to_coordinates(0) == (0, 0)
        assert self.sub_mt.convert_linear_number_to_coordinates(1) == (1, 0)
        assert self.sub_mt.convert_linear_number_to_coordinates(2) == (2, 0)
        assert self.sub_mt.convert_linear_number_to_coordinates(3) == (0, 1)
        assert self.sub_mt.convert_linear_number_to_coordinates(4) == (1, 1)
        assert self.sub_mt.convert_linear_number_to_coordinates(5) == (2, 1)

        for number in (-1, 6):
            with pytest.raises(IndexError):
                self.sub_mt.convert_linear_number_to_coordinates(number)

    def test_coordinates_to_number_conversions(self):
        assert self.sub_mt.convert_coordinates_to_linear_number(0, 0) == 0
        assert self.sub_mt.convert_coordinates_to_linear_number(1, 0) == 1
        assert self.sub_mt.convert_coordinates_to_linear_number(2, 0) == 2
        assert self.sub_mt.convert_coordinates_to_linear_number(0, 1) == 3
        assert self.sub_mt.convert_coordinates_to_linear_number(1, 1) == 4
        assert self.sub_mt.convert_coordinates_to_linear_number(2, 1) == 5

        for (col, row) in [(-1, 0), (0, -1), (3, 0), (0, 2)]:
            with pytest.raises(IndexError):
                self.sub_mt.convert_coordinates_to_linear_number(col, row)

    def test_make_tiling(self):
        tiling = self.sub_mt.tiling
        correct_tiling = [
            Cell(frozenset({self.mp_31c2}), frozenset()),
            MeshTiling.empty_cell,
            Cell(frozenset({self.mp_1c2}), frozenset()),
            MeshTiling.empty_cell,
            MeshTiling.point_cell,
            MeshTiling.empty_cell
        ]
        assert tiling == correct_tiling

    def test_invalid_obstruction(self):
        invalid_cell = Cell(frozenset({"not a mesh patt"}), frozenset())
        invalid_mt = MeshTiling({(0, 0): invalid_cell})
        with pytest.raises(ValueError):
            list(invalid_mt.get_subrules())

    def test_get_elmnts_of_size_Av21_cell(self):
        mt = MeshTiling({
            (0, 0): Cell(frozenset({Perm((1, 0))}), frozenset()),
            (1, 1): MeshTiling.point_cell
        })

        for size in range(1, 5):
            expected_perms = set(Av([Perm((1, 0))]).of_length(size))
            mt_perms = mt.get_elmnts(of_size=size)
            assert (len(set(mt_perms)) == len(list(mt_perms)))
            assert (set(mt_perms) == expected_perms)

    def test_get_elmnts_of_size_point_cell(self):
        mt = MeshTiling({
            (0, 0): MeshTiling.point_cell
        })

        for size in range(1, 5):
            expected_perms = {Perm((0,))} if size == 1 else set()
            mt_perms = mt.get_elmnts(of_size=size)
            assert (len(set(mt_perms)) == len(list(mt_perms)))
            assert (set(mt_perms) == expected_perms)

    def test_subrules(self):
        self.root_mt.MAX_COLUMN_DIMENSION = 3
        self.root_mt.MAX_ROW_DIMENSION = 2
        self.root_mt.MAX_ACTIVE_CELLS = 3
        subrules = list(self.root_mt.get_subrules())
        assert all(isinstance(rule, Rule) for rule in subrules)
        assert (self.empty_mt in subrules)
        assert (self.any_mt in subrules)
        assert (self.root_mt in subrules)
        assert (self.sub_mt in subrules)

    def test_subrules_too_small_dimensions(self):
        self.root_mt.MAX_COLUMN_DIMENSION = 2
        self.root_mt.MAX_ROW_DIMENSION = 2
        self.root_mt.MAX_ACTIVE_CELLS = 3
        subrules = list(self.root_mt.get_subrules())
        assert all(isinstance(rule, Rule) for rule in subrules)
        assert (self.empty_mt in subrules)
        assert (self.any_mt in subrules)
        assert (self.root_mt in subrules)
        assert (self.sub_mt not in subrules)

    def test_dimensions(self):
        assert (self.empty_mt.get_dimension() == (1, 1))
        assert (self.any_mt.get_dimension() == (1, 1))
        assert (self.root_mt.get_dimension() == (1, 1))
        assert (self.sub_mt.get_dimension() == (3, 2))

    def test_length(self):
        assert (len(self.empty_mt) == 1)
        assert (len(self.any_mt) == 1)
        assert (len(self.root_mt) == 1)
        assert (len(self.sub_mt) == 6)

    def test_is_hashable(self):
        self.empty_mt.__hash__()
        self.any_mt.__hash__()
        self.root_mt.__hash__()
        self.sub_mt.__hash__()

    def test_str(self):
        assert str(self.empty_mt) == "\n --- \n|   |\n --- \n"
        assert "| Av({}) |".format(repr(self.mp_31c2)) \
               in str(self.root_mt).split("\n")

    def test_av_12_perm_and_mesh_patts(self):
        p = Perm((0, 1))
        mesh_patts = {MeshPatt(p, ()), MeshPatt(p, [(1, 0), (1, 1), (1, 2)])}
        perms = {p}
        expected_output = {p}
        assert MeshTiling.clean_patts(perms, mesh_patts) == expected_output

    def test_all_length_one_mesh_patt(self):
        p = Perm((0,))
        perms = {p}
        mesh_patts = {
            MeshPatt(p, shading) for shading in [
                list((n % 2, n // 2) for n, b in enumerate(c) if b)
                for c in product([True, False], repeat=4)
            ]
        }
        output = MeshTiling.clean_patts(perms, mesh_patts)

        assert len(output) == 4
        for patt in output:
            assert patt in perms or patt in mesh_patts


if __name__ == '__main__':
    unittest.main()
