"""Per-frame camera smoothness for all 16 scene cameras, measured in screen terms (an orthographic camera has no depth):
pan speed in frame-widths per second, pan acceleration, zoom rate (%/s) and zoom acceleration. Cuts are detected and
excluded. Writes metadata/camera_check.json.
    blender -b scenes/BC002_WEWORK.blend --python scripts/camera_check.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import config as C  # noqa: E402
from toolkit import fcurves  # noqa: E402

LIMITS = {"pan_fw_s": 0.45, "pan_acc_fw_s2": 0.6, "zoom_pct_s": 9.0, "zoom_acc_pct_s2": 12.0}


def sample(sc):
    cam = sc.camera
    fx = {(fc.data_path, fc.array_index): fc for fc in fcurves(cam)}
    fs = {fc.data_path: fc for fc in fcurves(cam.data)}
    out = []
    for f in range(1, C.SCENE_FRAMES + 1):
        x = fx[("location", 0)].evaluate(f)
        y = fx[("location", 1)].evaluate(f)
        s = fs["ortho_scale"].evaluate(f)
        out.append((x, y, s))
    return out


if __name__ == "__main__":
    rep, flags = {}, []
    for n in range(1, 17):
        sc = bpy.data.scenes[f"SC{n:02d}"]
        p = sample(sc)
        v, z = [], []
        for i in range(1, len(p)):
            (x0, y0, s0), (x1, y1, s1) = p[i - 1], p[i]
            d = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            cut = d > 0.5 or abs(s1 - s0) / s0 > 0.03
            v.append(None if cut else d * C.FPS / s0)
            z.append(None if cut else (s1 - s0) / s0 * 100 * C.FPS)
        acc, zac = [], []
        for i in range(1, len(v)):
            if v[i] is not None and v[i - 1] is not None:
                acc.append(abs(v[i] - v[i - 1]) * C.FPS)
                zac.append(abs(z[i] - z[i - 1]) * C.FPS)
        r = {"cuts": sum(1 for a in v if a is None),
             "max_pan_fw_s": round(max(a for a in v if a is not None), 3),
             "max_pan_acc_fw_s2": round(max(acc), 3),
             "max_zoom_pct_s": round(max(abs(a) for a in z if a is not None), 2),
             "max_zoom_acc_pct_s2": round(max(zac), 2)}
        for k, lim in (("max_pan_fw_s", "pan_fw_s"), ("max_pan_acc_fw_s2", "pan_acc_fw_s2"), ("max_zoom_pct_s", "zoom_pct_s"),
                       ("max_zoom_acc_pct_s2", "zoom_acc_pct_s2")):
            if r[k] > LIMITS[lim]:
                flags.append(f"SC{n:02d} {k}={r[k]} > {LIMITS[lim]}")
        rep[f"SC{n:02d}"] = r
        print(f"SC{n:02d}", r)
    json.dump({"limits": LIMITS, "scenes": rep, "flags": flags}, open(os.path.join(C.P["meta"], "camera_check.json"), "w"), indent=1)
    print("FLAGS", flags)
