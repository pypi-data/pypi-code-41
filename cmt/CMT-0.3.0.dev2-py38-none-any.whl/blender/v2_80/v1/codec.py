import bpy

import cmt.blender.v2_80.utils as utils
from cmt.blender.v2_80.v1.add_objects import add_block, add_camera, add_dummy, add_player_start, add_sphere, add_sun, \
    get_color
from cmt.cmap.v1 import *


def decode(cmap: CMap_1):
    bpy.context.scene['cmap_identifier'] = cmap.identifier.value
    bpy.context.scene['cmap_format_version'] = cmap.format_version
    bpy.context.scene['cmap_name'] = cmap.name

    # add camera
    add_camera(cmap.camera_pos, cmap.camera_look, cmap.preview_cam_set)

    # add sun
    add_sun(cmap.sun_angle, cmap.sun_rotation)

    for ent in cmap.entities:
        if type(ent) == Block_1:
            utils.create_material(f"Block{ent.block_type.name}", get_color(ent.block_type))

            # get possible time of checkpoint or finish
            time = None
            if ent.block_type == BlockType_1.CHECKPOINT or ent.block_type == BlockType_1.FINISH:
                # finish index is every time the last
                idx = ent.checkpoint_nr if ent.block_type == BlockType_1.CHECKPOINT else -1
                if idx < len(cmap.checkpoint_times):
                    time = cmap.checkpoint_times[idx]

            add_block(ent, time)
        elif type(ent) == Sphere_1:
            utils.create_material('Sphere', (1, 0, 0, 1))
            add_sphere(ent)
        elif type(ent) == PlayerStart_1:
            utils.create_material('PlayerStart', (0.27, 0.949, 0.945, 1))
            add_player_start(ent)
        elif type(ent) == Dummy_1:
            utils.create_material('Dummy', (0.949, 0.49, 0.27, 1))
            add_dummy(ent)

    # set unit scale to the same as celaria ingame editor
    bpy.context.scene.unit_settings.scale_length = 10
