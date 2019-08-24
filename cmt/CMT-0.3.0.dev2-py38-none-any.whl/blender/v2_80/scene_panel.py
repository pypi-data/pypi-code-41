import bpy

from cmt.a_map import MapType


class MetadataProps(bpy.types.PropertyGroup):
    identifier: bpy.props.EnumProperty(
        items=tuple((str(typ.value), typ.name, f"Value: {typ.value}") for typ in MapType),
        name="Identifier",
        description="Map Identifier",
        default=MapType.CMAP.value
    )
    version: bpy.props.IntProperty(
        name="Version",
        description="Map Version",
        default=1,
        min=0,
        max=1
    )
    name: bpy.props.StringProperty(
        name="Name",
        description="Map Name",
        default="New Map"
    )


class ScenePanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Celaria Metadata"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw_header(self, context: bpy.types.Context):
        self.layout.prop(context.scene, 'use_cmt', text="")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.cmt_metadata, 'identifier')
        row.prop(scene.cmt_metadata, 'version')

        layout.separator()

        row = layout.row()
        row.prop(scene.cmt_metadata, 'name')

        layout.active = scene.use_cmt


def register():
    bpy.types.Scene.use_cmt = bpy.props.BoolProperty(
        name="use_cmt",
        description="Enable/Disable Celaria Metadata in Scene"
    )
    bpy.utils.register_class(MetadataProps)
    bpy.types.Scene.cmt_metadata = bpy.props.PointerProperty(name="cmt metadata", type=MetadataProps)
    bpy.utils.register_class(ScenePanel)


def unregister():
    pass  # TODO
