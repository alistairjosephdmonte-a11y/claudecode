"""Lists frames in which a document, placeholder or card is partially transparent (used to re-render only those frames
after the transparency-overlap fix).  blender -b scenes/BC002_WEWORK.blend --python scripts/affected_frames.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import config as C  # noqa: E402
from toolkit import fcurves  # noqa: E402

out = set()
for n in range(1, 17):
    sc = bpy.data.scenes[f"SC{n:02d}"]
    for o in sc.objects:
        nm = o.name[5:]
        if not (nm.startswith("D0") or nm.startswith("D1") or nm.startswith("P0") or nm.startswith("pborder") or nm.startswith("pmark")
                or o.get("overlay") or (o.parent and "card" in o.parent.name)):
            continue
        m = o.active_material
        fcs = [fc for fc in fcurves(m) if fc.data_path == "diffuse_color"] if m else []
        for fc in fcs:
            for f in range(1, C.SCENE_FRAMES + 1):
                if 0.002 < fc.evaluate(f) < 0.998:
                    for g in (f - 1, f, f + 1):
                        if 1 <= g <= C.SCENE_FRAMES:
                            out.add(C.scene_start(n) + g - 1)
json.dump(sorted(out), open("/tmp/ww_logs/affected.json", "w"))
print("AFFECTED", len(out))
