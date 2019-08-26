import unittest
from tests.util import *
from north_c9.util import Vector3
from north_c9.grid import Grid
from north_c9.deck import N9Deck, n9_deck


class GridTestSuite(unittest.TestCase):
    def test_deck(self):
        print("TEST DECK")
        assert_equal(N9Deck.A1, Vector3(375, -219))
        assert_equal(N9Deck.A2, Vector3(337.5, -219))
        assert_equal(N9Deck.A3, Vector3(300, -219))
        assert_equal(N9Deck.B1, Vector3(375, -181.5))
        assert_equal(N9Deck.B2, Vector3(337.5, -181.5))
        assert_equal(N9Deck.B3, Vector3(300, -181.5))
        assert_equal(N9Deck.Q21, Vector3(-375, 381))

        try:
            N9Deck.Q22
            raise AssertionError(f'N9Deck.Q22 is not unset')
        except AttributeError:
            pass

    def test_deck_grid(self):
        deck_grid = Grid(
            rows=21,
            columns=17,
            spacing=37.5,
            offset=Vector3(-375, -219)
        )
        assert_equal(deck_grid.locations['A1'], Vector3(375, -219))
        assert_equal(deck_grid.locations['A2'], Vector3(337.5, -219))
        assert_equal(deck_grid.locations['A3'], Vector3(300, -219))
        assert_equal(deck_grid.locations['B1'], Vector3(375, -181.5))
        assert_equal(deck_grid.locations['B2'], Vector3(337.5, -181.5))
        assert_equal(deck_grid.locations['B3'], Vector3(300, -181.5))

    def test_n9_grid_locations(self):
        for index, location in n9_deck.locations.items():
            assert_vector_equal(getattr(N9Deck, index), location)

    def test_grid(self):
        grid = Grid(2, 2, 10, Vector3(0, 0, 0))
        assert_equal(len(grid.grid), 2)
        assert_list_items_equal(grid.grid[0], [Vector3(10, 0, 0), Vector3(10, 10, 0)])
        assert_list_items_equal(grid.grid[1], [Vector3(0, 0, 0), Vector3(0, 10, 0)])

    def test_generate_class(self):
        grid = Grid(2, 2, 10, Vector3(0, 0, 0))
        source = grid.generate_class('GridTest', 'grid_test')
        assert_equal(source, """from north_c9.grid import Grid
from north_c9.util import Vector3


class GridTest(Grid):
    A1 = Vector3(x=10.0, y=0.0, z=0.0)
    B1 = Vector3(x=10.0, y=10.0, z=0.0)
    A2 = Vector3(x=0.0, y=0.0, z=0.0)
    B2 = Vector3(x=0.0, y=10.0, z=0.0)

    def __init__(self) -> None:
        Grid.__init__(self, rows=2, columns=2, spacing=10, offset=Vector3(x=0.0, y=0.0, z=0.0))


grid_test = GridTest()
""")