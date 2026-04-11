import bpy
from bpy.types import Panel

class VIEW3D_PT_UE5_Toolkit(Panel):
    bl_label = "UE5 Workflow Toolkit"
    bl_idname = "VIEW3D_PT_ue5_toolkit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE5 Export'

    def draw(self, context):
        layout = self.layout
        p = context.scene.ue5_data
        
        box = layout.box(); box.label(text="1. Visualization", icon='RESTRICT_VIEW_OFF'); box.operator("ue5.toggle_backface", icon='NORMALS_FACE')
        
        box = layout.box()
        box.label(text="2. Geometry Setup", icon='MESH_DATA')
        box.prop(p, "pivot_pos", text="")
        box.operator("ue5.prepare_geometry", icon='OBJECT_ORIGIN')
        box.operator("ue5.create_collision", icon='PHYSICS')
        
        box = layout.box(); box.label(text="3. Materials & Textures", icon='MATERIAL'); box.operator("ue5.rename_internal", icon='EVENT_M'); box.operator("ue5.save_textures", icon='FOLDER_REDIRECT')
        box = layout.box(); box.label(text="4. Export", icon='EXPORT'); box.prop(p, "light_intensity"); box.prop(p, "apply_transforms"); box.prop(p, "export_individual"); box.separator(); box.operator("ue5.export_fbx", icon='FILE_BACKUP')

def register():
    bpy.utils.register_class(VIEW3D_PT_UE5_Toolkit)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_UE5_Toolkit)