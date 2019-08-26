import unittest
from tests.util import *
from north_c9.kinematics import prrr_inverse_kinematics, prrr_forward_kinematics, PRRRBotConfiguration, PRRRBotDefinition
from north_c9.util import Vector3

zero_vector = Vector3(0, 0, 0)

bot_a = PRRRBotDefinition(column_offset=0, link1_length=5, link2_length=5, link3_length=0)
bot_b = PRRRBotDefinition(column_offset=0, link1_length=170.25, link2_length=170.25, link3_length=0)

zero_config = PRRRBotConfiguration(column=0, link1=0, link2=0, link3=0)
zero_config_position = Vector3(0, 10, 0)

simple_config = PRRRBotConfiguration(column=0, link1=math.pi/2, link2=math.pi/2, link3=0)
simple_config_position = Vector3(5, -5, 0)

class KinematicsTestSuite(unittest.TestCase):
    def test_forward_kinematics(self):
        position, rotation = prrr_forward_kinematics(bot_a, zero_config)
        assert_vector_equal(position, zero_config_position)

        position, rotation = prrr_forward_kinematics(bot_a, simple_config)
        assert_vector_equal(position, simple_config_position)

    def test_inverse_kinematics(self):
        config_a, config_b = prrr_inverse_kinematics(bot_a, zero_config_position, zero_vector, zero_vector)
        assert_config_equal(config_a, zero_config)
        assert_config_equal(config_b, zero_config)

        config_a, config_b = prrr_inverse_kinematics(bot_a, simple_config_position, Vector3(0, 0, math.pi), zero_vector)
        assert_config_equal(config_a, simple_config)

    def test_bot_b(self):
        position, rotation = prrr_forward_kinematics(bot_b, zero_config)
        assert_vector_equal(position, Vector3(0, 340.5, 0))

        config_a, config_b = prrr_inverse_kinematics(bot_b, Vector3(0, 340.5, 0), zero_vector, zero_vector)
        assert_config_equal(config_a, zero_config)

        config_a, config_b = prrr_inverse_kinematics(bot_b, Vector3(100, 100, 0), zero_vector, zero_vector)
        assert_config_equal(config_b, PRRRBotConfiguration(
            link1=1.9278841342163549, link2=-2.284971941637813, link3=-0.3570878074214583
        ))