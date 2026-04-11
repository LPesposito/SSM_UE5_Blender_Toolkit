import bpy
from bpy.props import FloatProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup

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

def register():
    bpy.utils.register_class(UE5_Toolkit_Data)
    bpy.types.Scene.ue5_data = PointerProperty(type=UE5_Toolkit_Data)

def unregister():
    bpy.utils.unregister_class(UE5_Toolkit_Data)
    del bpy.types.Scene.ue5_data