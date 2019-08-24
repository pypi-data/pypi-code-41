from typing import Tuple

import bpy
import math


def to_bl_location(location: Tuple[float, float, float]) -> Tuple[float, float, float]:
    # celarias Y coordinate is mirrored to the Blender
    return location[0] / 100, location[1] / -100, location[2] / 100


def to_cmt_position(location: Tuple[float, float, float]) -> Tuple[float, float, float]:
    # celarias Y coordinate is mirrored to the Blender
    return location[0] * 100, location[1] * -100, location[2] * 100


def to_bl_scale(scale: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return scale[0] / 100, scale[1] / 100, scale[2] / 100


def to_cmt_scale(scale: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return scale[0] * 100, scale[1] * 100, scale[2] * 100


def to_bl_rotation_z(rotation_z: float) -> float:
    return math.radians(rotation_z) * -1


def to_cmt_rotation_z(rotation_z: float) -> float:
    return math.degrees(rotation_z * -1)


def get_collection(name: str) -> bpy.types.Collection:
    """
    If the collection is not existing it will create a new.
    :param name:
    :return:
    """
    coll = bpy.data.collections.get(name, None)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)

    return coll


def add_exclusive_to_collection(obj: bpy.types.Object, coll_name: str):
    bpy.ops.collection.objects_remove_all()
    get_collection(coll_name).objects.link(obj)


def create_material(name: str, color: Tuple[float, float, float, float]) -> bpy.types.Material:
    """
    Creates a material with a specific color, if the material name does not already exist.
    :param name:
    :param color:
    :return:
    """
    mat = bpy.data.materials.get(name, None)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = color
    return mat
