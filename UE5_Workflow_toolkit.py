bl_info = {
    "name": "UE5 Workflow Toolkit",
    "author": "Lp Moonkey Dev",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > UE5 Export",
    "description": "Smart export and organization for Unreal Engine 5",
    "category": "Import-Export",
}

import bpy
import os
import re
import mathutils
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

# --- PROPERTIES ---
class UE5_Toolkit_Data(PropertyGroup):
    light_intensity: FloatProperty(name="Light Intensity", description="Multiplies light energy for UE5 (typical: 100-600)", default=100.0, min=0.0)
    apply_transforms: BoolProperty(name="Apply Transforms", description="Apply rotation/scale before export", default=True)
    export_individual: BoolProperty(name="Export Individual", description="Exports each object as a separate FBX", default=False)
    pivot_pos: EnumProperty(
        name="Pivot Position",
        items=[('NONE', "Keep Original", ""), ('CENTER', "Center", ""), ('BOTTOM', "Bottom", ""), 
               ('LEFT', "Left", ""), ('RIGHT', "Right", ""), ('FRONT', "Front", ""), ('BACK', "Back", "")],
        default='NONE'
    )

# --- UTILS ---
def find_image_node(input_pin):
    if not input_pin or not input_pin.is_linked: return None
    link = input_pin.links[0]
    node = link.from_node
    if node.type == 'TEX_IMAGE': return node
    for inp in node.inputs:
        if inp.is_linked:
            res = find_image_node(inp)
            if res: return res
    return None

# --- OPERATORS ---
class UE5_OT_ToggleBackface(Operator):
    """Toggle Backface Culling to find inverted faces"""
    bl_idname = "ue5.toggle_backface"
    bl_label = "Check Inverted Faces"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.show_backface_culling = not space.shading.show_backface_culling
        return {'FINISHED'}

class UE5_OT_PrepareGeometry(Operator):
    """Apply Scale/Rotation and move Pivot point"""
    bl_idname = "ue5.prepare_geometry"
    bl_label = "Fix Transforms & Pivot"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not objs: return {'CANCELLED'}
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        mode = context.scene.ue5_data.pivot_pos
        if mode == 'CENTER':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        elif mode != 'NONE':
            for obj in objs:
                context.view_layer.objects.active = obj
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                world_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
                offset = mathutils.Vector((0, 0, 0))
                if mode == 'BOTTOM': offset.z = obj.location.z - min(v.z for v in world_verts)
                elif mode == 'LEFT': offset.x = obj.location.x - min(v.x for v in world_verts)
                elif mode == 'RIGHT': offset.x = obj.location.x - max(v.x for v in world_verts)
                elif mode == 'FRONT': offset.y = obj.location.y - min(v.y for v in world_verts)
                elif mode == 'BACK': offset.y = obj.location.y - max(v.y for v in world_verts)
                if mode == 'BOTTOM': obj.location.z -= offset.z
                elif mode in ['LEFT', 'RIGHT']: obj.location.x -= offset.x
                elif mode in ['FRONT', 'BACK']: obj.location.y -= offset.y
                obj.data.transform(mathutils.Matrix.Translation(offset))
        return {'FINISHED'}

class UE5_OT_RenameInternal(Operator):
    """Rename Materials and Images internally based on connections"""
    bl_idname = "ue5.rename_internal"
    bl_label = "Rename Internally"
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
                    for pin, suffix in map_slots.items():
                        node = find_image_node(bsdf.inputs.get(pin))
                        if node and node.image: node.image.name = f"T_{mat.name}_{suffix}"
        return {'FINISHED'}

class UE5_OT_SaveTextures(Operator):
    """Save textures to disk and relink"""
    bl_idname = "ue5.save_textures"
    bl_label = "Save Textures"
    directory: StringProperty(subtype='DIR_PATH')
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    def execute(self, context):
        path = os.path.join(self.directory, "textures")
        if not os.path.exists(path): os.makedirs(path)
        for obj in context.selected_objects:
            for slot in obj.material_slots:
                if slot.material and slot.material.use_nodes:
                    for n in slot.material.node_tree.nodes:
                        if n.type == 'TEX_IMAGE' and n.image:
                            try:
                                f = os.path.join(path, n.image.name + ".png")
                                n.image.save_render(f)
                                n.image.filepath = f
                            except: pass
        return {'FINISHED'}

class UE5_OT_ExportFBX(Operator, ExportHelper):
    """Optimized FBX Export for UE5"""
    bl_idname = "ue5.export_fbx"
    bl_label = "Export FBX"
    filename_ext = ".fbx"
    def execute(self, context):
        p = context.scene.ue5_data
        for l in bpy.data.lights:
            if "op" not in l: l["op"] = l.energy
            l.energy = l["op"] * p.light_intensity
        bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection=True, global_scale=1.0, 
            apply_scale_options='FBX_SCALE_ALL' if p.apply_transforms else 'FBX_SCALE_NONE',
            bake_space_transform=True, object_types={'MESH', 'LIGHT', 'EMPTY'}, path_mode='COPY', 
            embed_textures=True, mesh_smooth_type='FACE')
        return {'FINISHED'}

# --- UI ---
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
        box = layout.box(); box.label(text="2. Geometry Setup", icon='MESH_DATA'); box.prop(p, "pivot_pos", text=""); box.operator("ue5.prepare_geometry", icon='OBJECT_ORIGIN')
        box = layout.box(); box.label(text="3. Materials & Textures", icon='MATERIAL'); box.operator("ue5.rename_internal", icon='EVENT_M'); box.operator("ue5.save_textures", icon='FOLDER_REDIRECT')
        box = layout.box(); box.label(text="4. Export", icon='EXPORT'); box.prop(p, "light_intensity"); box.prop(p, "apply_transforms"); box.prop(p, "export_individual"); box.separator(); box.operator("ue5.export_fbx", icon='FILE_BACKUP')

# --- REGISTRY ---
classes = (UE5_Toolkit_Data, UE5_OT_ToggleBackface, UE5_OT_PrepareGeometry, UE5_OT_RenameInternal, UE5_OT_SaveTextures, UE5_OT_ExportFBX, VIEW3D_PT_UE5_Toolkit)
def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.ue5_data = PointerProperty(type=UE5_Toolkit_Data)
def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "ue5_data"): del bpy.types.Scene.ue5_data
if __name__ == "__main__": register()