import bpy
import bmesh
import os
import re
import mathutils
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from .utils import find_image_node, setup_ue5_parenting

class UE5_OT_ToggleBackface(Operator):
    """Toggle Backface Culling to find inverted faces"""
    bl_idname = "ue5.toggle_backface"
    bl_label = "Check Inverted Faces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and len(context.selected_objects) >= 1

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
        selected_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        original_active = context.view_layer.objects.active
        method = context.scene.ue5_data.collision_method

        # Garantir a existência da coleção "Collisions"
        col_name = "Collisions"
        collision_col = bpy.data.collections.get(col_name)
        if not collision_col:
            collision_col = bpy.data.collections.new(col_name)
            context.scene.collection.children.link(collision_col)

        for obj in selected_meshes:
            clean_name = obj.name.replace(".", "_")

            if method == 'SMART_CONVEX':
                # --- UCX Logic ---
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                new_obj.name = f"UCX_{clean_name}"
                collision_col.objects.link(new_obj)
                new_obj.data.materials.clear()

                bm = bmesh.new()
                bm.from_mesh(new_obj.data)
                bmesh.ops.convex_hull(bm, input=bm.verts)
                bm.to_mesh(new_obj.data)
                bm.free()
                new_obj.data.update()

                decimate = new_obj.modifiers.new(name="UCX_Simplify", type='DECIMATE')
                decimate.ratio = 0.5
                context.view_layer.objects.active = new_obj
                bpy.ops.object.modifier_apply(modifier=decimate.name)
                setup_ue5_parenting(new_obj, obj)

            elif method == 'BOX':
                # --- UBX Logic (Single) ---
                new_obj = self.create_ubx_from_bounds(obj, f"UBX_{clean_name}", collision_col)
                setup_ue5_parenting(new_obj, obj)

            elif method == 'COMPOUND':
                # --- UBX Logic (Multi/Loose Parts) ---
                tmp_copy = obj.copy()
                tmp_copy.data = obj.data.copy()
                context.scene.collection.objects.link(tmp_copy)
                
                bpy.ops.object.select_all(action='DESELECT')
                tmp_copy.select_set(True)
                context.view_layer.objects.active = tmp_copy
                
                # Separa em partes soltas
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.mode_set(mode='OBJECT')
                
                parts = context.selected_objects
                for i, part in enumerate(parts):
                    ubx_name = f"UBX_{clean_name}_{i:02d}"
                    ubx_obj = self.create_ubx_from_bounds(part, ubx_name, collision_col)
                    setup_ue5_parenting(ubx_obj, obj)
                    bpy.data.objects.remove(part, do_unlink=True)

        # 6. Limpeza final da seleção (restaurar originais)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_meshes:
            obj.select_set(True)
        context.view_layer.objects.active = original_active

        return {'FINISHED'}

    def create_ubx_from_bounds(self, source_obj, name, collection):
        """Gera uma malha de cubo baseada na bounding box do objeto"""
        mesh = bpy.data.meshes.new(name)
        new_obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(new_obj)
        
        bm = bmesh.new()
        # Cria vértices nos 8 cantos da bounding box local
        for corner in source_obj.bound_box:
            bm.verts.new(corner)
        bm.verts.ensure_lookup_table()
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        
        new_obj.matrix_world = source_obj.matrix_world
        new_obj.data.materials.clear()
        return new_obj

class UE5_OT_RenameInternal(Operator):
    """Rename Materials and Images internally based on connections"""
    bl_idname = "ue5.rename_internal"
    bl_label = "Rename Internally"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Mapeamento com prioridade: Base Color por último para garantir que
        # se a imagem for compartilhada com Alpha, o sufixo final seja 'Color'.
        map_slots = [
            ('Alpha', 'A'),
            ('Metallic', 'Metallic'),
            ('Roughness', 'Roughness'),
            ('Normal', 'Normal'),
            ('Base Color', 'Color')
        ]
        processed_materials = set()

        for obj in context.selected_objects:
            if obj.type != 'MESH': continue
            c_obj_name = re.sub(r'\.\d{3}$', '', obj.name)

            for slot in obj.material_slots:
                mat = slot.material
                if not mat or mat in processed_materials: continue

                # Limpa o nome base do material (remove .001 e prefixos M_ existentes)
                m_base = re.sub(r'\.\d{3}$', '', mat.name)
                if m_base.startswith("M_"): m_base = m_base[2:]
                
                # Evita redundância caso o nome do objeto já esteja no nome do material
                if m_base.startswith(c_obj_name):
                    mat.name = f"M_{m_base}"
                else:
                    mat.name = f"M_{c_obj_name}_{m_base}"
                
                processed_materials.add(mat)
                if not mat.use_nodes: continue

                bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if bsdf:
                    tex_prefix = mat.name[2:] if mat.name.startswith("M_") else mat.name
                    for pin, suffix in map_slots:
                        node = find_image_node(bsdf.inputs.get(pin))
                        if node and node.image: 
                            node.image.name = f"T_{tex_prefix}_{suffix}"
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
        
        # Backup das configurações de render para restaurar após o processo
        render_settings = context.scene.render.image_settings
        old_format = render_settings.file_format
        old_color_mode = render_settings.color_mode

        for obj in context.selected_objects:
            for slot in obj.material_slots:
                if slot.material and slot.material.use_nodes:
                    for n in slot.material.node_tree.nodes:
                        if n.type == 'TEX_IMAGE' and n.image:
                            img = n.image
                            try:
                                f = os.path.join(path, img.name + ".png")
                                # Configura formato para PNG e preserva Alpha se a imagem possuir
                                render_settings.file_format = 'PNG'
                                render_settings.color_mode = 'RGBA' if (img.channels == 4 or img.use_alpha) else 'RGB'
                                
                                img.save_render(f)
                                img.filepath = f
                            except: pass
        
        # Restaura as configurações originais do usuário
        render_settings.file_format = old_format
        render_settings.color_mode = old_color_mode
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

        # Armazena energias originais para restaurar depois
        original_energies = {l: l.energy for l in bpy.data.lights}
        for l in bpy.data.lights:
            l.energy *= p.light_intensity

        export_dir = os.path.dirname(self.filepath)
        export_count = 0

        if p.export_individual:
            for obj in selected_objs:
                if obj.type != 'MESH': continue
                
                # 1. Salvar estado original
                original_loc = obj.location.copy()
                
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                # Selecionar filhos (Colisões) para exportarem junto
                for child in obj.children:
                    if child.name.startswith(("UCX_", "UBX_", "USP_", "UCP_")):
                        child.select_set(True)
                
                try:
                    # 2. Mover temporariamente para (0,0,0)
                    obj.location = (0, 0, 0)
                    
                    # 3. Aplicar transformações (Rotação e Escala)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    
                    # 4. Exportar
                    obj_path = os.path.join(export_dir, f"{obj.name}.fbx")
                    bpy.ops.export_scene.fbx(
                        filepath=obj_path,
                        use_selection=True,
                        global_scale=1.0,
                        apply_scale_options='FBX_SCALE_ALL',
                        axis_forward='-Z',
                        axis_up='Y',
                        bake_space_transform=True,
                        object_types={'MESH', 'LIGHT', 'EMPTY'},
                        path_mode='COPY',
                        embed_textures=True,
                        mesh_smooth_type='FACE'
                    )
                    export_count += 1
                finally:
                    # 5. Restaurar posição original
                    obj.location = original_loc
            
            self.report({'INFO'}, "Success: %d individual FBX files generated." % export_count)
        else:
            # Exportação de Grupo (Cena Completa)
            bpy.ops.export_scene.fbx(
                filepath=self.filepath,
                use_selection=True,
                global_scale=1.0,
                apply_scale_options='FBX_SCALE_ALL',
                axis_forward='-Z',
                axis_up='Y',
                bake_space_transform=True,
                object_types={'MESH', 'LIGHT', 'EMPTY'},
                path_mode='COPY',
                embed_textures=True,
                mesh_smooth_type='FACE'
            )
            self.report({'INFO'}, "Group export finished.")
        
        # Restaura as energias originais após o export
        for l, energy in original_energies.items():
            l.energy = energy
            
        return {'FINISHED'}

classes = (UE5_OT_ToggleBackface, UE5_OT_PrepareGeometry, UE5_OT_CreateCollision, UE5_OT_RenameInternal, UE5_OT_SaveTextures, UE5_OT_ExportFBX)

def register():
    for cls in classes: bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)