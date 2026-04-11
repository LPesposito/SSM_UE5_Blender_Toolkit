# UE5 Workflow Toolkit for Blender

A tool built to automate the migration and export process from Blender to Unreal Engine 5. It handles naming conventions, texture management, and coordinate system alignment.

### Context
During the port of a legacy project from **Blender Game Engine** to **UE5**, we faced constant issues with:
* Disorganized texture naming (e.g., `color.002.png`).
* Missing textures on FBX export.
* Incorrect light scales (Blender vs Unreal physical units).
* Pivot points and transforms mismatch.

---

## Features

### 1. Pivot & Geometry
* **Advanced Pivot Snapping:** Set origin to Bottom (Floor), Center, Left, Right, Front, or Back based on world bounds.
* **Batch Transform:** Applies Scale and Rotation while preserving smooth shading settings.

### 2. Smart Material Logic
* **Connection-Based Renaming:** Instead of reading node labels, the script analyzes the **Principled BSDF** inputs. It identifies maps connected to *Base Color*, *Metallic*, *Roughness*, and *Normal* sockets.
* **Naming Pattern:** 
  * Materials: `M_[ObjectName]`
  * Textures: `T_[MaterialName]_[MapType]`

### 3. Texture Management
* **Internal Rename:** Cleans up the `.blend` data block names.
* **Physical Export:** Saves connected textures into a `/textures` subfolder at a chosen path, relinking them automatically.

### 4. UE5 Optimized Export
* **Light Multiplier:** Converts Blender light energy to Unreal's intensity.
* **Individual Export:** Each selected mesh is exported as its own FBX file named after the object.

---

## Installation

1. Download `ue5_toolkit.py`.
2. Blender > Preferences > Add-ons > Install.
3. Activate **Export: UE5 Workflow Toolkit**.
4. Find the panel in the **3D Viewport Sidebar (N)** under the **UE5 Export** tab.

---

## Usage
1. **Setup:** Select meshes and set the desired pivot (e.g., *Bottom* for props). Click **Fix Transforms & Pivot**.
2. **Materials:** Use **Rename Internally** to standardize your data.
3. **Textures:** Use **Save Textures to Disk** to organize your external files.
4. **Final Export:** Adjust **Light Intensity** (default 100x) and click **Export FBX**.

---

## License
MIT
