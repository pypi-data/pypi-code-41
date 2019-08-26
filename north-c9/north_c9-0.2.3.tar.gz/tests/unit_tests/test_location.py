import unittest
from tests.util import *
from north_c9.location import Frame, Location


class LocationTestSuite(unittest.TestCase):
    def test_rotation_x(self):
        assert_vector_equal(Location(1, 1, 0).rotate_x(90), Location(1, 0, 1))

    def test_rotation_y(self):
        assert_vector_equal(Location(1, 1, 0).rotate_y(90), Location(0, 1, -1))

    def test_rotation_z(self):
        assert_vector_equal(Location(1, 1, 0).rotate_z(90), Location(-1, 1, 0))

    def test_rotation(self):
        assert_vector_equal(Location(1, 1, 0).rotate(Location(90, 0, 0)), Location(1, 0, 1))
        assert_vector_equal(Location(1, 1, 0).rotate(Location(0, 90, 0)), Location(0, 1, -1))
        assert_vector_equal(Location(1, 1, 0).rotate(Location(0, 0, 90)), Location(-1, 1, 0))

    def test_transform(self):
        assert_vector_equal(Location(1, 1, 1).transform(Location(90, 0, 0), Location(0, 0, -1)), Location(1, -1, 0))
        assert_vector_equal(Location(1, 1, 1).transform(Location(0, 90, 0), Location(0, 0, -1)), Location(1, 1, -2))
        assert_vector_equal(Location(1, 1, 1).transform(Location(0, 0, 90), Location(0, 0, -1)), Location(-1, 1, 0))
        
    def test_frame_translation(self):
        frame = Frame(Location(1, 1, 0))
        assert_equal(frame.parent, Frame.WORLD)
        location = Location(1, 1, 1, frame=frame)
        assert_vector_equal(location.world_location, Location(2, 2, 1))

    def test_frame_rotation(self):
        frame = Frame(Location(0, 0, 0), Location(0, 0, 90))
        location = Location(1, 1, 0, frame=frame)
        assert_vector_equal(location.world_location, Location(-1, 1, 0))

    def test_frame_transform(self):
        frame = Frame(Location(1, 1, 0), Location(0, 0, 90))
        location = Location(1, 1, 0, frame=frame)
        assert_vector_equal(location.world_location, Location(0, 2, 0))

    def test_position_frame_transform(self):
        parent_frame = Frame(Location(1, 1, 0), Location(0, 0, 90))
        child_frame = Frame(Location(1, 1, 0), Location(0, 0, 90), parent_frame)
        location = Location(1, 1, 0, frame=child_frame)
        assert_vector_equal(location.world_location, Location(-1, 1, 0))
