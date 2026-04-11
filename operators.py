import bpy
import os
import re
import mathutils
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from .utils import find_image_node

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

class UE5_OT_CreateCollision(Operator):
    """Create UCX collision mesh for selected objects"""
    bl_idname = "ue5.create_collision"
    bl_label = "Create UCX Collision"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']
        for obj in selected:
            new_data = obj.data.copy()
            clean_name = re.sub(r'\.\d{3}$', '', obj.name)
            new_obj = bpy.data.objects.new(name=f"UCX_{clean_name}", object_data=new_data)
            context.collection.objects.link(new_obj)
            new_obj.matrix_world = obj.matrix_world
            new_obj.data.materials.clear()
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
        selected_objs = context.selected_objects
        if not selected_objs: return {'CANCELLED'}

        for l in bpy.data.lights:
            if "op" not in l: l["op"] = l.energy
            l.energy = l["op"] * p.light_intensity

        export_dir = os.path.dirname(self.filepath)
        if p.export_individual:
            for obj in selected_objs:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                obj_path = os.path.join(export_dir, f"{obj.name}.fbx")
                bpy.ops.export_scene.fbx(filepath=obj_path, use_selection=True, global_scale=1.0, 
                    apply_scale_options='FBX_SCALE_ALL' if p.apply_transforms else 'FBX_SCALE_NONE',
                    bake_space_transform=True, object_types={'MESH', 'LIGHT', 'EMPTY'}, path_mode='COPY', 
                    embed_textures=True, mesh_smooth_type='FACE')
            for obj in selected_objs: obj.select_set(True)
        else:
            bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection=True, global_scale=1.0, 
                apply_scale_options='FBX_SCALE_ALL' if p.apply_transforms else 'FBX_SCALE_NONE',
                bake_space_transform=True, object_types={'MESH', 'LIGHT', 'EMPTY'}, path_mode='COPY', 
                embed_textures=True, mesh_smooth_type='FACE')
        return {'FINISHED'}

classes = (UE5_OT_ToggleBackface, UE5_OT_PrepareGeometry, UE5_OT_CreateCollision, UE5_OT_RenameInternal, UE5_OT_SaveTextures, UE5_OT_ExportFBX)

def register():
    for cls in classes: bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)