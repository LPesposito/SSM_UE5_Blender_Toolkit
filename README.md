[Read this in Portuguese (Brasil)](README.pt-br.md)

# Scene StaticMesh - UE5 Workflow Toolkit

A professional Blender addon designed to automate the organization and export of complex scenes or individual Static Meshes to Unreal Engine 5. It ensures industry-standard naming conventions, optimized collisions, and perfect coordinate alignment.

### Why this tool?
Developed to solve critical pipeline friction when moving assets to **UE5**, specifically addressing:
* **Pivot Mismatch:** Automatic centering to world origin during export.
* **Collision Management:** Automated UCX/UBX generation with geometric simplification.
* **Material Complexity:** Smart renaming for objects with multiple material slots.
* **Coordinate Systems:** Fixed -Z Forward / Y Up orientation.
* **Physical Units:** Light energy conversion between Blender and Unreal.

---

## Features

### 1. Geometry & Precision Pivot
* **Advanced Pivot Snapping:** Set origin to Bottom (Floor), Center, Left, Right, Front, or Back.
* **Origin-Zero Export:** In Individual Mode, the tool temporarily moves each asset to (0,0,0) during export, ensuring the UE5 pivot matches your Blender setup exactly.

### 2. Automated Collisions (UCX/UBX)
* **Smart Convex (UCX):** Generates simplified convex hulls (50% decimation) for performance.
* **Box (UBX):** Creates perfect box collisions based on object bounds.
* **Compound Box:** Automatically separates loose parts and generates individual UBX boxes for complex shapes.

### 3. Advanced Material & Texture Naming
* **Multi-Material Support:** Handles objects with multiple slots using the `M_[ObjectName]_[MaterialName]` pattern.
* **Duplicate Prevention:** Tracks processed materials to avoid redundant renaming.
* **Texture Pattern:** `T_[MaterialName]_[Suffix]` (e.g., `T_Wall_Brick_Normal`).

### 4. UE5 Optimized Export
* **Axis Correction:** Native -Z Forward and Y Up export settings.
* **Individual Batch Export:** Exports every selected mesh as a unique FBX, automatically including its collision children.

---

## Installation

1. Download the repository as a ZIP.
2. In Blender: **Edit > Preferences > Add-ons > Install**.
3. Select the ZIP file and activate **Import-Export: SSM - UE5 Workflow Toolkit**.
4. Access the tool in the **Sidebar (N)** under the **UE5 Export** tab.

---

## Usage

1. **Visualization:** Toggle Backface Culling to catch flipped normals before they reach Unreal.
2. **Geometry:** Set your pivot, fix transforms, and choose your collision method (UCX/UBX).
3. **Materials & Textures:** Standardize names and export textures to a dedicated folder.
4. **Export:** Set light intensity multiplier and choose between Group or Individual export.

---

## Credits
Developed with ❤️ by **Lp Moonkey Dev**.