"""Renders the in-game 'gameplay' shown on CRT_01 from frame 385: CAR_01_GAMEPLAY cruising up Ocean Drive.
    blender -b scenes/PS_GTA_EP01_BLOCK.blend --python scripts/render_gameplay.py
Writes textures/gameplay/g_0385.png ... g_0480.png (640x480) with a simple original radar HUD."""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

sc = bpy.context.scene
bpy.data.collections["GAMEPLAY_ONLY"].hide_render = False
for n in ("FX_magenta_fog", "FX_transition_fog"):
    bpy.data.objects[n].hide_render = True
sc.timeline_markers.clear()
sc.camera = bpy.data.objects["CAM_GAMEPLAY"]
sc.render.resolution_x, sc.render.resolution_y = 640, 480
sc.eevee.taa_render_samples = 16
out = os.path.join(C.P["tex"], "gameplay")
os.makedirs(out, exist_ok=True)
for f in range(385, C.TOTAL_FRAMES + 1):
    p = os.path.join(out, f"g_{f:04d}.png")
    if os.path.exists(p):
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
