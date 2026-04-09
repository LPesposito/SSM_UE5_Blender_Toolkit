bl_info = {
    "name": "UE5 Workflow Toolkit",
    "author": "Lp Moonkey",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > UE5 Export Tab",
    "description": "Refactored toolkit: Logic by node connection + separated export",
    "category": "Export",
}

import bpy
import os
import re
import mathutils
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

# --- UTILS ---
def find_image_node(input_pin):
    """Trace back from a pin to find the connected Image Texture node"""
    if not input_pin or not input_pin.is_linked:
        return None
    
    node = input_pin.links[0].from_node
    
    # Direct connection
    if node.type == 'TEX_IMAGE':
        return node
    
    # Connection through Normal Map, Color Ramp or Math nodes
    for input in node.inputs:
        if input.is_linked:
            recursive_search = find_image_node(input)
            if recursive_search: return recursive_search
    return None

# --- PROPERTIES ---
class UE5_Toolkit_Data(PropertyGroup):
    light_intensity: FloatProperty(name="Light Intensity", default=100.0, min=0.0)
    apply_transforms: BoolProperty(name="Apply Transforms", default=True)
    export_individual: BoolProperty(name="Export Individual", default=False)
    pivot_pos: EnumProperty(
        name="Pivot Position",
        items=[('NONE', "Keep Original", ""), ('CENTER', "Center", ""), ('BOTTOM', "Bottom", "")],
        default='NONE'
    )

# --- OPERATORS ---

class UE5_OT_ToggleBackface(Operator):
    """Toggle Backface Culling"""
    bl_idname = "ue5.toggle_backface"
    bl_label = "Check Inverted Faces"
    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.show_backface_culling = not space.shading.show_backface_culling
        return {'FINISHED'}

class UE5_OT_PrepareGeometry(Operator):
    """Fix Transforms and Pivot"""
    bl_idname = "ue5.prepare_geometry"
    bl_label = "Fix Transforms & Pivot"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = context.selected_objects
        if not objs: return {'CANCELLED'}
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        mode = context.scene.ue5_data.pivot_pos
        if mode == 'CENTER':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        elif mode == 'BOTTOM':
            for obj in objs:
                if obj.type != 'MESH': continue
                context.view_layer.objects.active = obj
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                z_min = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
                offset = obj.location.z - z_min
                obj.data.transform(mathutils.Matrix.Translation((0, 0, offset)))
                obj.location.z = z_min
        return {'FINISHED'}

class UE5_OT_RenameInternal(Operator):
    """Rename Materials and Images internally based on Principled BSDF connections"""
    bl_idname = "ue5.rename_internal"
    bl_label = "Rename Materials & Textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        map_slots = {'Base Color': 'Color', 'Metallic': 'Metallic', 'Roughness': 'Roughness', 'Normal': 'Normal'}
        
        for obj in context.selected_objects:
            if obj.type != 'MESH': continue
            c_name = re.sub(r'\.\d{3}$', '', obj.name)
            
            for slot in obj.material_slots:
                mat = slot.material
                if not mat or not mat.use_nodes: continue
                mat.name = f"M_{c_name}"
                
                bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if bsdf:
                    for pin_name, suffix in map_slots.items():
                        img_node = find_image_node(bsdf.inputs.get(pin_name))
                        if img_node and img_node.image:
                            img_node.image.name = f"T_{mat.name}_{suffix}"
        return {'FINISHED'}

class UE5_OT_SaveTextures(Operator):
    """Export textures of selected objects to a physical folder"""
    bl_idname = "ue5.save_textures"
    bl_label = "Select Folder"
    directory: StringProperty(subtype='DIR_PATH')
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    def execute(self, context):
        tex_path = os.path.join(self.directory, "textures")
        if not os.path.exists(tex_path): os.makedirs(tex_path)
        
        for obj in context.selected_objects:
            if obj.type != 'MESH': continue
            for slot in obj.material_slots:
                if slot.material and slot.material.use_nodes:
                    for node in slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            try:
                                p = os.path.join(tex_path, node.image.name + ".png")
                                node.image.save_render(p)
                                node.image.filepath = p
                            except: pass
        return {'FINISHED'}

class UE5_OT_ExportFBX(Operator, ExportHelper):
    """Export to FBX"""
    bl_idname = "ue5.export_fbx"
    bl_label = "Export FBX"
    filename_ext = ".fbx"
    def execute(self, context):
        props = context.scene.ue5_data
        for light in bpy.data.lights:
            if "orig_p" not in light: light["orig_p"] = light.energy
            light.energy = light["orig_p"] * props.light_intensity
        bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection=True, global_scale=1.0, 
            apply_scale_options='FBX_SCALE_ALL' if props.apply_transforms else 'FBX_SCALE_NONE',
            bake_space_transform=True, object_types={'MESH', 'LIGHT', 'EMPTY'}, path_mode='COPY', 
            embed_textures=True, mesh_smooth_type='FACE')
        return {'FINISHED'}

# --- UI ---

class VIEW3D_PT_UE5_Toolkit(Panel):
    bl_label = "UE5 Workflow Toolkit"
    bl_idname = "VIEW3D_PT_ue5_toolkit_final"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UE5 Export'

    def draw(self, context):
        layout = self.layout
        props = context.scene.ue5_data
        
        box = layout.box()
        box.label(text="1. Visualization", icon='RESTRICT_VIEW_OFF')
        box.operator("ue5.toggle_backface", icon='NORMALS_FACE')
        
        box = layout.box()
        box.label(text="2. Geometry Setup", icon='MESH_DATA')
        box.prop(props, "pivot_pos", text="")
        box.operator("ue5.prepare_geometry", icon='OBJECT_ORIGIN')
        
        box = layout.box()
        box.label(text="3. Materials & Textures", icon='MATERIAL')
        box.operator("ue5.rename_internal", text="Rename Internally", icon='EVENT_M')
        box.operator("ue5.save_textures", text="Save Textures to Disk", icon='FOLDER_REDIRECT')
        
        box = layout.box()
        box.label(text="4. Export", icon='EXPORT')
        box.prop(props, "light_intensity")
        box.prop(props, "apply_transforms")
        box.prop(props, "export_individual")
        box.separator()
        box.operator("ue5.export_fbx", icon='FILE_BACKUP')

# --- REGISTRY ---
classes = (UE5_Toolkit_Data, UE5_OT_ToggleBackface, UE5_OT_PrepareGeometry, UE5_OT_RenameInternal, UE5_OT_SaveTextures, UE5_OT_ExportFBX, VIEW3D_PT_UE5_Toolkit)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.ue5_data = PointerProperty(type=UE5_Toolkit_Data)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ue5_data

if __name__ == "__main__":
    register()