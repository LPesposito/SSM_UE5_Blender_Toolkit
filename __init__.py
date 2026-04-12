bl_info = {
    "name": "SSM - UE5 Workflow Toolkit",
    "author": "Lp Moonkey Dev",
    "version": (2, 0, 0),
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
    bpy.app.translations.register(__name__, utils.translations_dict)

def unregister():
    bpy.app.translations.unregister(__name__)
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()