"""Checks the rendered frames: completeness (11,520 files, 1920x1080), unexpected jumps (frame-to-frame change outside
known cuts), unexpected black frames, and the background colour. Writes metadata/frame_check.json.
    python3 scripts/frame_check.py"""
import json
import os

import numpy as np
from PIL import Image

import config as C

if __name__ == "__main__":
    log = json.load(open(os.path.join(C.P["meta"], "build_log.json")))
    cuts = set()
    for name, lg in log.items():
        n = int(name[2:])
        cuts.add(C.scene_start(n))
        for seg in lg["shots"][1:]:
            cuts.add(C.scene_start(n) + int(round(seg[0][0] * C.FPS)))
    missing, badsize, jumps, black, prev = [], [], [], [], None
    diffs = {}
    bg = []
    per = {}
    for f in range(1, C.TOTAL_FRAMES + 1):
        p = os.path.join(C.P["frames"], f"f_{f:04d}.png")
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            missing.append(f)
            prev = None
            continue
        im = Image.open(p)
        if im.size != tuple(C.RES):
            badsize.append(f)
        if f % 240 == 1:
            bg.append(int(np.asarray(im.convert("RGB"))[540:560, 4:24].mean()))
        a = np.asarray(im.convert("L").resize((96, 54), Image.BILINEAR), dtype=np.float32)
        if a.max() < 12:
            black.append(f)
        if prev is not None:
            d = float(np.abs(a - prev).mean())
            sc = (f - 1) // C.SCENE_FRAMES + 1
            per[sc] = max(per.get(sc, 0), d if f not in cuts else 0)
            diffs[f] = d
        prev = a
    # a jump is a single-frame spike: much larger than both neighbours' change (smooth fades change steadily)
    for f, d in diffs.items():
        nb = [diffs.get(f - 1, 0), diffs.get(f + 1, 0)]
        if f not in cuts and d > 4.0 and d > 2.5 * max(max(nb), 0.5):
            jumps.append((f, round(d, 2)))
    # black frames are expected only inside deliberate fades at act boundaries and the final fade-out
    allowed = set()
    for a in C.ACTS:
        e = C.scene_start(a[2][-1]) + C.SCENE_FRAMES
        allowed |= set(range(e - 16, e + 16))
    allowed |= set(range(1, 60))
    for n in range(1, 17):                            # each scene opens on black before its first fade-in
        allowed |= set(range(C.scene_start(n), C.scene_start(n) + 14))
    out = {"frames_expected": C.TOTAL_FRAMES, "frames_present": C.TOTAL_FRAMES - len(missing), "missing": missing[:50],
           "wrong_size": badsize[:50], "unexpected_jumps": jumps[:50],
           "unexpected_black_frames": [f for f in black if f not in allowed][:50],
           "background_mean_8bit": round(float(np.mean(bg)), 2) if bg else None, "background_target": "#080808 = 8",
           "known_cuts": len(cuts), "per_scene_max_change": {f"SC{k:02d}": round(v, 2) for k, v in sorted(per.items())}}
    out["pass"] = not (out["missing"] or out["wrong_size"] or out["unexpected_jumps"] or out["unexpected_black_frames"])
    json.dump(out, open(os.path.join(C.P["meta"], "frame_check.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_scene_max_change"}, indent=1))
