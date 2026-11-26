"""Extracts sound and camera events from the baked sim to metadata/events.json.

    blender -b scenes/trap_chain.blend --python scripts/events.py

snap:   a trap's bar leaves its latched position (bar angle relative to base passes 30 degrees)
clack:  a base, bar or ball reverses its downward velocity (a landing or bounce), with impact speed
"""

import json
import math
import os

import bpy
import numpy as np

sc = bpy.context.scene
F = sc.frame_end
dt = sc.render.fps_base / sc.render.fps
bases = sorted((o for o in bpy.data.objects if o.name.endswith("_Base")), key=lambda o: o.name)
bodies = [o for o in bpy.data.objects if o.animation_data and o.animation_data.action
          and not o.name.startswith("CAM")]
pos = {o.name: np.zeros((F, 3)) for o in bodies}
ang = {o.name: np.zeros(F) for o in bases}
for f in range(1, F + 1):
    sc.frame_set(f)
    for o in bodies:
        pos[o.name][f - 1] = o.matrix_world.translation
    for o in bases:
        bar = bpy.data.objects[o.name.replace("_Base", "_Bar")]
        r = (o.matrix_world.inverted() @ bar.matrix_world).to_3x3()
        ang[o.name][f - 1] = math.degrees(math.acos(max(-1, min(1, r[0][0]))))
ev = {"fps": sc.render.fps, "frames": F, "snap": [], "clack": [], "paths": {}}
for o in bases:
    a = ang[o.name]
    hit = np.nonzero(a > 30)[0]
    if len(hit):
        f = int(hit[0]) + 1
        ev["snap"].append({"frame": f, "name": o.name, "pos": pos[o.name][f - 1].round(3).tolist()})
for name, p in pos.items():
    vz = np.diff(p[:, 2]) / dt
    kind = "ball" if name.startswith("BALL") else "pingpong" if name.startswith("PINGPONG") else \
        "bar" if name.endswith("_Bar") else "base"
    for f in range(1, len(vz)):
        if vz[f - 1] < -0.08 and vz[f] > vz[f - 1] * 0.3 and p[f, 2] < 0.12:
            ev["clack"].append({"frame": f + 1, "kind": kind, "speed": round(float(-vz[f - 1]), 3),
                                "pos": p[f].round(3).tolist()})
    if kind in ("ball",):
        ev["paths"][name] = p[::6].round(3).tolist()
ev["snap"].sort(key=lambda e: e["frame"])
ev["clack"].sort(key=lambda e: e["frame"])
out = os.path.join(os.path.dirname(bpy.data.filepath), "..", "metadata", "events.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(ev, open(out, "w"), indent=0)
print("EVENTS snaps %d clacks %d" % (len(ev["snap"]), len(ev["clack"])), flush=True)
