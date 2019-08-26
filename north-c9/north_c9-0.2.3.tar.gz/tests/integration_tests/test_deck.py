import os
import unittest
import time
from ..util import *
from .. import mock_client
from north_c9.controller import C9Controller
from north_c9.robot import N9Robot, N9RobotMovementUnreachableLocation
from north_c9.util import Vector3, ZERO_VECTOR
from north_c9.grid import Grid
from north_c9.deck import n9_deck

mocked_client = os.environ.get('C9_MOCK_CLIENT', '') == 'True'
client = mock_client.C9Client() if mocked_client else None
controller = C9Controller(client=client)
robot = N9Robot(controller=controller, velocity_counts=5000, acceleration_counts=5000)


class DeckTestSuite(unittest.TestCase):
    def test_grid_locations(self):
        for index, location in n9_deck.locations.items():
            if not mocked_client:
                print(f'Moving to: {index} ({location})')

            try:
                location.z = 300
                robot.move_to_location(location, ZERO_VECTOR)
                time.sleep(1)
                #robot_location, robot_rotation = robot.forward_kinematics()
                #assert_vector_equal(robot_location, location, diff=0.00000000001)
            except N9RobotMovementUnreachableLocation:
                if not mocked_client:
                    print(' - unreachable')