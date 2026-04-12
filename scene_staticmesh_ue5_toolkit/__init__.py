bl_info = {
    "name": "SSM - UE5 Workflow Toolkit",
    "author": "Lp Moonkey Dev",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > UE5 Export",
    "description": "Smart export and organization for Unreal Engine 5",
    "warning": "",
    "doc_url": "https://github.com/LPesposito/SSM_UE5_Blender_Toolkit",
    "category": "Import-Export",
    "license": "GPL-3.0-or-later",
}

# Suporte a recarregamento de scripts (Reload Scripts)
if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(utils)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from .scene_staticmesh_ue5_toolkit import operators

import bpy
from .scene_staticmesh_ue5_toolkit import properties, ui, utils

def register():
    properties.register()
    operators.register()
    ui.register()
    bpy.app.translations.register(__name__, utils.translations_dict)

def unregister():
    bpy.app.translations.unregister(__name__)
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()