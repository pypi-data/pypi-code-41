import bpy

from cmt.cmap.v1 import *


class BlockProps(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        items=tuple((str(typ.value), typ.name.title(), f"Value: {typ.value}") for typ in BlockType_1),
        name="Type",
        default=str(BlockType_1.NOTHING.value)
    )

    checkpoint_nr: bpy.props.IntProperty(
        name="Number",
        description="Checkpoint Number",
        default=0,
        min=0
    )


class Dummy(bpy.types.PropertyGroup):
    id: bpy.props.IntProperty(
        name="ID",
        description="ID",
        default=0,
        min=0
    )


class ObjectPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Celaria Object"
    bl_idname = "OBJECT_PT_cmt"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        typ = context.object.type
        return context.scene.use_cmt and (typ == 'MESH' or typ == 'CAMERA' or typ == 'LIGHT')

    def draw_header(self, context: bpy.types.Context):
        self.layout.prop(context.object, 'use_cmt', text="")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.prop(obj, 'cmt_entity')
        layout.separator()

        if obj.cmt_entity == 'block':
            row = layout.row()
            row.prop(obj.cmt_block, 'type')
            if obj.cmt_block.type == str(BlockType_1.CHECKPOINT.value):
                row = layout.row()
                row.prop(obj.cmt_block, 'checkpoint_nr')
        elif obj.cmt_entity == '':
            pass

        # Big render button
        layout.label(text="Big Button:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("render.render")

        # Different sizes in a row
        layout.label(text="Different button sizes:")
        row = layout.row(align=True)
        row.operator("render.render")

        sub = row.row()
        sub.scale_x = 2.0
        sub.operator("render.render")

        row.operator("render.render")

        layout.active = obj.use_cmt


def register(version: int = 1):
    bpy.types.Object.use_cmt = bpy.props.BoolProperty(
        name='use_cmt',
        description="Enable/Disable Celaria Object"
    )
    bpy.types.Object.cmt_entity = bpy.props.EnumProperty(
        items=(('block', 'Block', ''), ('sphere', 'Sphere', ''), ('playerstart', 'PlayerStart', ''), ('dummy', 'Dummy', '')),
        name='Entity',
        description='Entity',
        default='block'
    )
    bpy.utils.register_class(BlockProps)
    bpy.types.Object.cmt_block = bpy.props.PointerProperty(name="cmt_v1_block", type=BlockProps)
    bpy.utils.register_class(ObjectPanel)


def unregister():
    pass  # TODO


# TODO: only development, remove later
if __name__ == "__main__":
    register()
