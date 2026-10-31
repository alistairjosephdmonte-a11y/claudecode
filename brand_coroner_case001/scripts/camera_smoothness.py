"""Per-frame camera smoothness from the evaluated camera transform (constraints included).
    blender -b scenes/BC001_MASTER.blend --python scripts/camera_smoothness.py
Writes metadata/camera_smoothness.json. Flags: position acc > 2 m/s^2, angular acc > 60 deg/s^2,
ortho zoom acc > 2 %/s^2, or a velocity jump (jerk spike) between consecutive frames."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import config as C  # noqa: E402

sc = bpy.context.scene
FPS = C.FPS
res, flags = {}, []
for s in C.SHOTS:
    cam = bpy.data.objects[s["camera"]]
    P, F, U, O = [], [], [], []
    for f in range(s["frame_start"], s["frame_end"] + 1):
        sc.frame_set(f)
        m = cam.matrix_world
        P.append(m.translation.copy())
        F.append((m.to_3x3() @ Vector((0, 0, -1))).normalized())
        U.append((m.to_3x3() @ Vector((0, 1, 0))).normalized())
        O.append(cam.data.ortho_scale if cam.data.type == "ORTHO" else 0.0)
    n = len(P)
    v = [(P[i + 1] - P[i]) * FPS for i in range(n - 1)]
    a = [(v[i + 1] - v[i]).length * FPS for i in range(n - 2)]
    j = [abs(a[i + 1] - a[i]) * FPS for i in range(len(a) - 1)]
    w = [math.degrees(F[i].angle(F[i + 1], 0) + 0.5 * U[i].angle(U[i + 1], 0)) * FPS for i in range(n - 1)]
    wa = [abs(w[i + 1] - w[i]) * FPS for i in range(len(w) - 1)]
    oz = [(O[i + 1] - O[i]) / O[0] * 100 * FPS for i in range(n - 1)] if O[0] else [0.0]
    oza = [abs(oz[i + 1] - oz[i]) * FPS for i in range(len(oz) - 1)] if O[0] else [0.0]
    r = dict(camera=cam.name, type=cam.data.type, move=cam.get("move", ""), travel_m=round((P[-1] - P[0]).length, 3),
             max_speed_m_s=round(max(x.length for x in v), 4), max_acc_m_s2=round(max(a), 4), max_jerk=round(max(j), 2),
             max_ang_deg_s=round(max(w), 3), max_angacc_deg_s2=round(max(wa), 2),
             ortho_zoom_pct_s=round(max(abs(x) for x in oz), 3), ortho_zoom_acc=round(max(oza), 3),
             start_speed=round(v[0].length, 4), end_speed=round(v[-1].length, 4))
    bad = []
    if r["max_acc_m_s2"] > 2.0:
        bad.append("position acceleration")
    if r["max_angacc_deg_s2"] > 60:
        bad.append("angular acceleration")
    if r["ortho_zoom_acc"] > 2.0:
        bad.append("zoom acceleration")
    med = sorted(a)[len(a) // 2] if a else 0
    spikes = [s["frame_start"] + 1 + i for i, x in enumerate(a) if x > max(5 * med, 0.5)]
    if spikes:
        bad.append(f"acceleration spike at {spikes[:3]}")
    r["result"] = "smooth" if not bad else "; ".join(bad)
    res[s["shot_id"]] = r
    if bad:
        flags.append((s["shot_id"], r["result"]))
json.dump(dict(thresholds="acc <= 2 m/s^2, angular acc <= 60 deg/s^2, zoom acc <= 2 %/s^2, no acceleration spikes", flags=flags, shots=res),
          open(os.path.join(C.P["metadata"], "camera_smoothness.json"), "w"), indent=1)
for k, r in res.items():
    print("CAM", k, r["type"][:5], f"travel {r['travel_m']:7.2f} m  v {r['max_speed_m_s']:6.3f}  a {r['max_acc_m_s2']:6.3f}  "
          f"w {r['max_ang_deg_s']:6.2f}  wa {r['max_angacc_deg_s2']:6.2f}  zoom {r['ortho_zoom_pct_s']:5.2f}%/s  {r['result']}")
print("FLAGS", flags)
