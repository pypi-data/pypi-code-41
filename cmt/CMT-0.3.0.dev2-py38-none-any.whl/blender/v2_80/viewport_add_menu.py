from typing import Set

import bpy

from cmt.blender.v2_80 import utils
from cmt.blender.v2_80.v1.add_objects import add_block, add_dummy, add_player_start, add_sphere, get_color
from cmt.cmap.v1 import *


class AddNewBlock(bpy.types.Operator):
    """Add a new Block"""
    bl_idname = "cmt.add_new_block"
    bl_label = "Add a new Celaria Block"

    block_types: bpy.props.EnumProperty(
        items=tuple((str(typ.value), typ.name.title(), f"Value: {typ.value}") for typ in BlockType_1),
        name="Type",
        default=str(BlockType_1.NOTHING.value)
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        ent = Block_1()
        ent.block_type = BlockType_1(int(self.block_types))
        ent.scale = utils.to_cmt_scale((1, 1, 1))
        ent.position = utils.to_cmt_position(bpy.context.scene.cursor.location)
        utils.create_material(f"Block{ent.block_type.name}", get_color(ent.block_type))
        add_block(ent)
        return {'FINISHED'}


class AddNewSphere(bpy.types.Operator):
    """Add a new Sphere"""
    bl_idname = "cmt.add_new_sphere"
    bl_label = "Add a new Celaria Sphere"

    def execute(self, context: bpy.types.Context) -> Set[str]:
        ent = Sphere_1()
        ent.position = utils.to_cmt_position(bpy.context.scene.cursor.location)
        utils.create_material('Sphere', (1, 0, 0, 1))
        add_sphere(ent)
        return {'FINISHED'}


class AddNewPlayerStart(bpy.types.Operator):
    """Add a new Player Start"""
    bl_idname = "cmt.add_new_playerstart"
    bl_label = "Add a new Celaria Player Start"

    def execute(self, context: bpy.types.Context) -> Set[str]:
        ent = PlayerStart_1()
        ent.position = utils.to_cmt_position(bpy.context.scene.cursor.location)
        utils.create_material('PlayerStart', (0.27, 0.949, 0.945, 1))
        add_player_start(ent)
        return {'FINISHED'}


class AddNewDummy(bpy.types.Operator):
    """Add a new Dummy"""
    bl_idname = "cmt.add_new_dummy"
    bl_label = "Add a new Celaria Dummy"

    def execute(self, context: bpy.types.Context) -> Set[str]:
        ent = Dummy_1()
        ent.position = utils.to_cmt_position(bpy.context.scene.cursor.location)
        utils.create_material('Dummy', (0.949, 0.49, 0.27, 1))
        add_dummy(ent)
        return {'FINISHED'}


class ViewportAddMenu(bpy.types.Menu):
    """Create new Celaria Objects"""
    bl_idname = "VIEW3D_MT_add_cmt"
    bl_label = "Celaria Objects"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.operator_menu_enum(AddNewBlock.bl_idname, 'block_types', text="Block...", icon='MESH_CUBE')
        layout.operator(AddNewSphere.bl_idname, text='Sphere', icon='MESH_ICOSPHERE')
        layout.operator(AddNewPlayerStart.bl_idname, text='Player Start', icon='OUTLINER_OB_ARMATURE')
        layout.operator(AddNewDummy.bl_idname, text='Dummy', icon='MESH_UVSPHERE')


def menu_add_object(self, context: bpy.types.Context):
    self.layout.separator()
    self.layout.menu(ViewportAddMenu.bl_idname)


def register():
    bpy.utils.register_class(ViewportAddMenu)
    bpy.utils.register_class(AddNewBlock)
    bpy.utils.register_class(AddNewSphere)
    bpy.utils.register_class(AddNewPlayerStart)
    bpy.utils.register_class(AddNewDummy)
    bpy.types.VIEW3D_MT_add.append(menu_add_object)


def unregister():
    pass  # TODO
