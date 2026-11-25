"""Look pass applied to the saved scene: darker floor, lower fill, AgX contrast. Shared by build_sim.py and re-runnable.

    blender -b scenes/trap_chain.blend --python scripts/grade.py
"""

import bpy


def grade():
    sc = bpy.context.scene
    nt = bpy.data.materials["MAT_Floor_Planks"].node_tree
    br = next(n for n in nt.nodes if n.type == "TEX_BRICK")
    br.inputs["Color1"].default_value = (0.085, 0.045, 0.022, 1)
    br.inputs["Color2"].default_value = (0.13, 0.07, 0.035, 1)
    br.inputs["Mortar"].default_value = (0.02, 0.012, 0.007, 1)
    bpy.data.materials["MAT_Wall_Plaster"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.32, 0.30, 0.25, 1)
    bpy.data.lights["FILL"].energy = 35
    bpy.data.lights["KEY_Window"].energy = 600
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.0


if __name__ == "__main__":
    grade()
    bpy.ops.wm.save_mainfile(compress=True)
    print("GRADED", flush=True)
