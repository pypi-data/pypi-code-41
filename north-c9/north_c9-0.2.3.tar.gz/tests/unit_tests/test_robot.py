import unittest
from tests import mock_client
from tests.util import *
from north_c9 import robot, kinematics, controller
from north_c9.util import Vector3

home_config = kinematics.PRRRBotConfiguration(
    column=304.8,
    link1=-2.0465765369860796,
    link2=-2.5544228266482656,
    link3=0
)


def move_test(robot, location, rotation, config):
    robot.move_to_location(location, rotation)
    assert_config_equal(robot.configuration, config)


class RobotTestSuite(unittest.TestCase):
    def setUp(self):
        self.client = mock_client.C9Client()
        self.controller = controller.C9Controller(client=self.client)
        self.robot = robot.N9Robot(self.controller)

    def tearDown(self):
        self.client.disconnect()

    def test_init(self):
        assert_config_equal(self.robot.configuration, home_config)

    def test_move(self):
        move_test(self.robot, Vector3(100, 100, 304.8), Vector3(0, 0, 0), kinematics.PRRRBotConfiguration(
            column=304.8, link1=1.9278841342163549, link2=-2.284971941637813, link3=-0.3570878074214583
        ))

        move_test(self.robot, Vector3(-100, 200, 304.8), Vector3(0, 0, 0), kinematics.PRRRBotConfiguration(
            column=304.8, link1=0.39071237206491666, link2=-1.7087199621314455, link3=-1.318007590066529
        ))

        with self.controller.trace_trajectories() as trajectories:
            self.robot.move_to_location(Vector3(-100, 200, 304.8), Vector3(0, 0, 0))

            link1_distance = trajectories[2].distance
            link2_distance = trajectories[1].distance

            assert_float_equal(link1_distance, 26617)
            assert_float_equal(link2_distance, 6865)

            assert_list_items_equal(trajectories[2].mopy, [1, 0, 150000, 6750, 45000, 0, 13117, 45000, -150000, 6750])
            assert_list_items_equal(trajectories[1].mopy, [1, 0, 38682, 1741, 11605, 0, 3383, 11605, -38682, 1741])
