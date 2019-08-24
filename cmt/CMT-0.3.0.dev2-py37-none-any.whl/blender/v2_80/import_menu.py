from pathlib import Path
from typing import Set

import bpy
import bpy_extras

import cmt
from cmt.a_map import MapType
from cmt.blender.v2_80.v1.codec import decode as decode_1


class ImportCMap(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """
    Import menu for .cmap or .ecmap file.
    """
    bl_idname = "import_scene.cmap"
    bl_label = "Import Celaria Map (.cmap/.ecmap)"

    # ImportHelper mixin class uses this
    filename_ext = ".cmap;.ecmap"

    filter_glob: bpy.props.StringProperty(
        default="*.cmap;*.ecmap",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        try:
            import_cmap(self, context, self.filepath)
        except Exception as ex:
            self.report({'ERROR'}, str(ex))
            return {'CANCELLED'}
        return {'FINISHED'}


def import_cmap(ops: ImportCMap, context: bpy.types.Context, filepath: Path):
    cmap = cmt.decode(Path(filepath))

    # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    if cmap.identifier == MapType.CMAP:
        ops.report({'INFO'}, f"{cmap.identifier.name} v{cmap.format_version} | '{cmap.name}' parsed.")
        if cmap.format_version == 1:
            decode_1(cmap)
            return
    raise ValueError(f"{cmap.identifier.name} v{cmap.format_version} is not supported.")


def menu_func_import(self, context: bpy.types.Context):
    self.layout.operator(ImportCMap.bl_idname, text="Celaria Map (.cmap/.ecmap)")


def register():
    bpy.utils.register_class(ImportCMap)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    pass  # TODO
