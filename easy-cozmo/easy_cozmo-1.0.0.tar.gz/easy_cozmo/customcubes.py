#!/usr/bin/env python3

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps, radians
import math
import time
import sys
import asyncio
from cozmo.objects import CustomObject, LightCube

from .say import *
from .say import _say_error

from . import mindcraft
from .movements import *
import numpy as np

from .mindcraft_defaults import df_scan_object_speed,\
        df_use_headlight_for_scan_object,\
        df_move_relative_refined,\
        df_align_distance,\
        df_align_refined,\
        df_forget_old_when_scanning_objects, \
        df_reverse_speed, \
        df_use_distance_threshold_for_objects, \
        df_distance_threshold_for_objects

from .actions_with_objects import _get_visible_object, \
        _get_visible_objects, \
        _scan_for_object, \
        _align_with_object, \
        _move_relative_to_object, \
        _get_relative_pose, \
        _get_nearest_object, \
        _align_with_nearest_object

_custom_cubes = []
def initialize_custom_cubes(cubes):
        global _custom_cubes
        _custom_cubes = cubes
        
def _is_custom_cube(obj):
        return obj is not None \
                and isinstance(obj, CustomObject) \
                and obj.object_type in _custom_cubes

def _get_visible_custom_cube():
        return _get_visible_object(_is_custom_cube, use_distance_threshold=True)

def _get_visible_custom_cubes():
        return _get_visible_objects(_is_custom_cube, use_distance_threshold=True)

def scan_for_custom_cube(angle, scan_speed=20):
        
        """**Rotate in place while looking for an object**

        This function executes a rotation, with certain angular speed
        and angle, while at the same time looking for an object.  As
        soon as Cozmo identifies a object in its field of view (not
        necessarily at the center of the camera), it stops.  As a
        result, Cozmo will keep seeing the object after it stops.

        :param angle: Angle to scan
        :type angle: float

            ..  note::

                If the angle is positive, Cozmo rotates in clockwise order. A negative angle is a counter clockwise rotation.

        :return: True (suceeded) or False (failed).
        """
        
        if not _scan_for_object(angle, valid_object_check=_is_custom_cube,
                                use_distance_threshold = True):
                return

        object = _get_visible_custom_cube()
        if not object:
                _say_error("I couldn't find a landmark, sorry")
                return False
        else:
                for i in range(3):
                        time.sleep(1)
                        if object.pose.origin_id != -1:
                                break
                if object.pose.origin_id == -1:
                        _say_error("I couldn't localize landmark, sorry")
                        return False

        return True

def _move_relative_to_custom_cube(customcube, pose, refined=df_move_relative_refined):
        return _move_relative_to_object(customcube, pose, refined)


def align_with_nearest_custom_cube(distance= df_align_distance):
        """**Align with nearest object**

        Takes Cozmo toward the nearest object, and aligns to it

        :param distance: Desired distance between Cozmo and the object
        :type distance: float

        :return: True (suceeded) or False (failed) """
        return _align_with_nearest_object(distance, valid_object_check=_is_custom_cube, refined=True, use_distance_threshold = True)

def align_with_custom_cube(cube, distance=df_align_distance):
        return _align_with_object(cube, distance=distance, valid_object_check=_is_custom_cube, refined=True, use_distance_threshold = True)

def _pickup_visible_custom_cube(cube, num_retries = 4):
        robot = mindcraft._mycozmo
        if not _is_custom_cube(cube):
                _say_error("Invalid cube ")
                return False
        action=None
        cubetype = cube.object_type
        try:
                for i in range(num_retries):
                        if not align_with_custom_cube(cube, distance=80):
                                _say_error("Can't align")
                                return False
                        move_lift_ground()
                        move_forward(6)
                        move_lift_up()
                        reverse(8)
                        objs = _get_visible_objects(valid_object_check=_is_custom_cube, use_distance_threshold = True)
                        picked = True
                        for obj in objs:
                                print("found object ", obj)
                                if obj.object_type != cubetype:
                                        continue
                                translation = robot.pose - obj.pose
                                dst = translation.position.x ** 2 + translation.position.y ** 2
                                dst = dst ** 0.5
                                if dst < 150:
                                        picked = False
                                        break
                        if picked:
                                return True
        except Exception as e:
                import traceback
                print(e)
                traceback.print_exc()
                _say_error("Pickup failed")                
        return False

def pickup_custom_cube():
        mindcraft._mycozmo.set_head_angle(degrees(0)).wait_for_completed()
        mindcraft._mycozmo.set_head_light(False)
        cube = _get_visible_custom_cube()
        if cube is None:
                _say_error("I can't see cube ", cube_id)
                return False
        return _pickup_visible_custom_cube(cube)
