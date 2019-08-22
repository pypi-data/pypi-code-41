import unittest
from tests.util import *
from north_c9 import trajectory


class TrajectoryTestSuite(unittest.TestCase):
    def test_trajectory_acceleration_triangular(self):
        traj = trajectory.Trajectory.acceleration_triangular(0, 10, 10)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_equal(len(traj.steps), 2)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, -10, 5])

        traj = trajectory.Trajectory.acceleration_triangular(10, 10, 10)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_list_items_equal(traj.steps[0].vap, [10, 0, 0])
        assert_list_items_equal(traj.steps[1].vap, [10, 0, 0])

        traj = trajectory.Trajectory.acceleration_triangular(10, 0, 10)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_list_items_equal(traj.steps[0].vap, [10, -10, 5])
        assert_list_items_equal(traj.steps[1].vap, [0, 10, 5])

        traj = trajectory.Trajectory.acceleration_triangular(10, 0, 10, direction=trajectory.Direction.REVERSE)
        assert_equal(traj.direction, trajectory.Direction.REVERSE)

    def test_trajectory_distance_triangular(self):
        traj = trajectory.Trajectory.distance_triangular(0, 10, 10)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, -10, 5])

        traj = trajectory.Trajectory.distance_triangular(0, 10, -10)
        assert_equal(traj.direction, trajectory.Direction.REVERSE)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, -10, 5])

        traj = trajectory.Trajectory.distance_triangular(0, 10, 9)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_list_items_equal(traj.steps[0].vap, [0, 12, 4])
        assert_list_items_equal(traj.steps[1].vap, [10, -12, 5])

    def test_trajectory_trapezoidal(self):
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 100)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_equal(len(traj.steps), 3)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, 0, 90])
        assert_list_items_equal(traj.steps[2].vap, [10, -10, 5])

        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, -99)
        assert_equal(traj.direction, trajectory.Direction.REVERSE)
        assert_equal(len(traj.steps), 3)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, 0, 89])
        assert_list_items_equal(traj.steps[2].vap, [10, -10, 5])

        # should fall back to a triangular trajectory if the distance isn't long enough to ramp up fully
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 10)
        assert_equal(len(traj.steps), 2)
        assert_equal(traj.direction, trajectory.Direction.FORWARD)
        assert_list_items_equal(traj.steps[0].vap, [0, 10, 5])
        assert_list_items_equal(traj.steps[1].vap, [10, -10, 5])

    def test_trajectory_duration(self):
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 100)
        assert_equal(traj.duration, 11.0)

        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, -99)
        assert_equal(traj.duration, 10.9)

        # should fall back to a triangular trajectory if the distance isn't long enough to ramp up fully
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 10)
        assert_equal(traj.duration, 2.0)

    def test_trajectory_distance(self):
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 100)
        assert_equal(traj.distance, 100)

        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, -99)
        assert_equal(traj.distance, 99)

        # should fall back to a triangular trajectory if the distance isn't long enough to ramp up fully
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 10)
        assert_equal(traj.distance, 10)

    def test_trajectory_mopy(self):
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 100)
        assert_list_items_equal(traj.mopy, [1, 0, 10, 5, 10, 0, 90, 10, -10, 5])

        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, -99)
        assert_list_items_equal(traj.mopy, [0, 0, 10, 5, 10, 0, 89, 10, -10, 5])

        # should fall back to a triangular trajectory if the distance isn't long enough to ramp up fully
        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 10)
        assert_list_items_equal(traj.mopy, [1, 0, 10, 5, 10, -10, 5])

        traj = trajectory.Trajectory.trapezoidal(0, 10, 10, 9)
        assert_list_items_equal(traj.mopy, [1, 0, 12, 4, 10, -12, 5])