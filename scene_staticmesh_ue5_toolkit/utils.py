def find_image_node(input_pin):
    if not input_pin or not input_pin.is_linked: return None
    link = input_pin.links[0]
    node = link.from_node
    if node.type == 'TEX_IMAGE': return node
    for inp in node.inputs:
        if inp.is_linked:
            res = find_image_node(inp)
            if res: return res

def setup_ue5_parenting(child, parent):
    """Configura o parentesco e inverte a matriz para evitar deslocamentos"""
    if child and parent:
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()
    return None

translations_dict = {
    "en_US": {
        ("*", "Check Inverted Faces"): "Check Inverted Faces",
        ("*", "Fix Transforms & Pivot"): "Fix Transforms & Pivot",
        ("*", "Create UCX Collision"): "Create UCX Collision",
        ("*", "Rename Internally"): "Rename Internally",
        ("*", "Save Textures"): "Save Textures",
        ("*", "Export FBX"): "Export FBX",
        ("*", "1. Visualization"): "1. Visualization",
        ("*", "2. Geometry Setup"): "2. Geometry Setup",
        ("*", "3. Materials & Textures"): "3. Materials & Textures",
        ("*", "4. Export"): "4. Export",
    },
    "pt_BR": {
        ("*", "Check Inverted Faces"): "Verificar Faces Invertidas",
        ("*", "Toggle Backface Culling to find inverted faces"): "Alternar Backface Culling para encontrar faces invertidas",
        ("*", "Fix Transforms & Pivot"): "Corrigir Transforms e Pivô",
        ("*", "Apply Scale/Rotation and move Pivot point"): "Aplicar Escala/Rotação e mover ponto de Pivô",
        ("*", "Create UCX Collision"): "Criar Colisão UCX",
        ("*", "Create UCX collision mesh for selected objects"): "Criar malha de colisão UCX para objetos selecionados",
        ("*", "Rename Internally"): "Renomear Internamente",
        ("*", "Rename Materials and Images internally based on connections"): "Renomear Materiais e Imagens internamente com base em conexões",
        ("*", "Save Textures"): "Salvar Texturas",
        ("*", "Save textures to disk and relink"): "Salvar texturas no disco e revincular",
        ("*", "Export FBX"): "Exportar FBX",
        ("*", "Optimized FBX Export for UE5"): "Exportação FBX otimizada para UE5",
        ("*", "1. Visualization"): "1. Visualização",
        ("*", "2. Geometry Setup"): "2. Configuração de Geometria",
        ("*", "3. Materials & Textures"): "3. Materiais e Texturas",
        ("*", "4. Export"): "4. Exportar",
        ("*", "Light Intensity"): "Intensidade da Luz",
        ("*", "Multiplies light energy for UE5 (typical: 100-600)"): "Multiplica a energia da luz para a UE5 (típico: 100-600)",
        ("*", "Apply Transforms"): "Aplicar Transformações",
        ("*", "Apply rotation/scale before export"): "Aplicar rotação/escala antes de exportar",
        ("*", "Export Individual"): "Exportar Individual",
        ("*", "Exports each object as a separate FBX"): "Exporta cada objeto como um FBX separado",
        ("*", "Pivot Position"): "Posição do Pivô",
        ("*", "Collision Method"): "Método de Colisão",
        ("*", "Keep Original"): "Manter Original",
        ("*", "Center"): "Centro",
        ("*", "Bottom"): "Base",
        ("*", "No mesh selected."): "Nenhuma malha selecionada.",
        ("*", "Success: %d individual FBX files generated."): "Sucesso: %d arquivos FBX individuais gerados.",
        ("*", "Group export finished."): "Exportação de grupo concluída.",
    }
}
