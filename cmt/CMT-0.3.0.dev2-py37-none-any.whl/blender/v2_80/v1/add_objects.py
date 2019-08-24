import math
from typing import Tuple

import bpy

from cmt.blender.v2_80 import utils
from cmt.cmap.v1 import *


def get_color(typ: BlockType_1) -> Tuple[float, float, float, float]:
    """
    Get the color of a specific block.
    """
    if BlockType_1.NOTHING == typ:
        return 1, 1, 1, 1
    elif BlockType_1.FINISH == typ:
        return 1, 0, 0, 1
    elif BlockType_1.JUMP == typ:
        return 0, 1, 0, 1
    elif BlockType_1.SPEED == typ:
        return 1, 1, 0, 1
    elif BlockType_1.ICE == typ:
        return 0, 0, 1, 1
    elif BlockType_1.CHECKPOINT == typ:
        return 0.5, 0, 0.5, 1
    return 0, 0, 0, 1


def add_block(ent: Block_1, time: CheckpointTime_1 = None) -> bpy.types.Object:
    """
    Add a block to collection.
    :return Created object.
    """
    # create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=utils.to_bl_location(ent.position))
    # resize
    bpy.ops.transform.resize(value=utils.to_bl_scale(ent.scale))
    # rotate
    bpy.ops.transform.rotate(value=utils.to_bl_rotation_z(ent.rotation_z), orient_axis='Z', orient_type='GLOBAL',
                             use_accurate=True)

    obj = bpy.context.active_object

    # add material
    obj.data.materials.append(bpy.data.materials[f"Block{ent.block_type.name}"])
    # change name
    obj.name = 'Block'
    # add custom properties
    obj['cmap_object'] = 'entity'
    obj['entity'] = 'block'
    obj['block_type'] = ent.block_type.value
    if ent.block_type == BlockType_1.CHECKPOINT or ent.block_type == BlockType_1.FINISH:
        if ent.block_type == BlockType_1.CHECKPOINT:
            obj['checkpoint_nr'] = ent.checkpoint_nr
        if time is not None:
            obj['time_platin'] = time.platin
            obj['time_gold'] = time.gold
            obj['time_silver'] = time.silver
            obj['time_bronze'] = time.bronze
        else:
            obj['time_platin'] = 0
            obj['time_gold'] = 0
            obj['time_silver'] = 0
            obj['time_bronze'] = 0

    # add to block collection
    utils.add_exclusive_to_collection(obj, 'Blocks')
    return obj


def add_sphere(ent: Sphere_1) -> bpy.types.Object:
    # create sphere
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=utils.to_bl_location(ent.position))
    # resize
    bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))

    obj = bpy.context.active_object

    # add delta location to make the sphere floating, where it is in game
    obj.delta_location[2] = 0.1
    # add material
    obj.data.materials.append(bpy.data.materials['Sphere'])
    # change name
    obj.name = 'Sphere'
    # add custom properties
    obj['cmap_object'] = 'entity'
    obj['entity'] = 'sphere'

    # add to spheres collection
    utils.add_exclusive_to_collection(obj, 'Spheres')
    return obj


def add_player_start(ent: PlayerStart_1):
    # create cone
    bpy.ops.mesh.primitive_cone_add(radius1=1, location=utils.to_bl_location(ent.position))
    # resize
    bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))
    # rotate
    bpy.ops.transform.rotate(value=utils.to_bl_rotation_z(ent.rotation_z), orient_axis='Z', orient_type='GLOBAL',
                             use_accurate=True)

    obj = bpy.context.active_object

    # add delta location to make the cone floating
    obj.delta_location[2] = 0.1
    # delta rotation, to rotate the top into looking direction
    obj.delta_rotation_euler[1] = math.radians(90)
    # add material
    obj.data.materials.append(bpy.data.materials['PlayerStart'])
    # change name
    obj.name = 'PlayerStart'
    # add custom properties
    obj['cmap_object'] = 'entity'
    obj['entity'] = 'playerstart'
    # add to playerstarts collection
    utils.add_exclusive_to_collection(obj, 'PlayerStarts')
    return obj


def add_dummy(ent: Dummy_1) -> bpy.types.Object:
    # create cone
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=utils.to_bl_location(ent.position))
    # resize
    bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))
    # rotate
    bpy.ops.transform.rotate(value=utils.to_bl_rotation_z(ent.rotation_z), orient_axis='Z', orient_type='GLOBAL',
                             use_accurate=True)

    obj = bpy.context.active_object

    # add material
    obj.data.materials.append(bpy.data.materials['Dummy'])
    # change name
    obj.name = 'Dummy'
    # add custom properties
    obj['cmap_object'] = 'entity'
    obj['entity'] = 'dummy'
    # add to Dummies collection
    utils.add_exclusive_to_collection(obj, 'Dummies')
    return obj


def add_camera(position: Tuple[float, float, float], look_at: Tuple[float, float, float],
               preview_cam_set: bool) -> bpy.types.Object:
    # add look at position
    bpy.ops.object.add(location=utils.to_bl_location(look_at))
    look_obj = bpy.context.active_object
    # change name
    look_obj.name = 'LookAt'
    look_obj['cmap_object'] = 'camera_look_at'
    # add to PreviewCamera collection
    utils.add_exclusive_to_collection(bpy.context.active_object, 'PreviewCamera')

    # add camera
    bpy.ops.object.camera_add(location=utils.to_bl_location(position))
    # setup tracking to look at
    bpy.ops.object.constraint_add(type='TRACK_TO')
    obj = bpy.context.active_object
    obj.constraints["Track To"].target = look_obj
    obj.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    obj.constraints["Track To"].up_axis = 'UP_Y'
    # add custom properties
    obj['cmap_object'] = 'camera'
    obj['preview_set'] = preview_cam_set
    # add to PreviewCamera collection
    utils.add_exclusive_to_collection(obj, 'PreviewCamera')
    return obj


def add_sun(angle: float, rotation_z: float) -> bpy.types.Object:
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50),
                             rotation=(0, math.radians(angle), utils.to_bl_rotation_z(rotation_z)))
    obj = bpy.context.active_object
    # add custom properties
    obj['cmap_object'] = 'sun'
    # add to root scene collection
    bpy.ops.collection.objects_remove_all()
    bpy.context.scene.collection.objects.link(obj)
    return obj
