bl_info = {
    "name": "Scene StaticMesh - UE5 Workflow Toolkit",
    "author": "Lp Moonkey Dev",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > UE5 Export",
    "description": "Smart export and organization for Unreal Engine 5",
    "category": "Import-Export",
}

# Suporte a recarregamento de scripts (Reload Scripts)
if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(utils)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import properties, utils, operators, ui

import bpy

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()