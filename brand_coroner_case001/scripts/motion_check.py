"""Frame-to-frame picture change over the animatic; flags jumps/pops inside shots (cuts excluded) and frozen shots."""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

d = os.path.join(C.P["previews"], "animatic_frames")
load = lambda i: np.asarray(Image.open(os.path.join(d, f"frame_{i:04d}.png")).convert("L").resize((160, 90)), dtype=np.float32)  # noqa: E731
diffs, prev = {}, load(1)
for i in range(2, C.TOTAL_FRAMES + 1):
    cur = load(i)
    diffs[i] = float(np.abs(cur - prev).mean())
    prev = cur
cuts = {s["frame_start"] for s in C.SHOTS}
flags, shots = [], {}
for s in C.SHOTS:
    vals = [diffs[f] for f in range(s["frame_start"] + 1, s["frame_end"] + 1)]
    shots[s["shot_id"]] = dict(mean=round(float(np.mean(vals)), 3), max=round(float(np.max(vals)), 2), static_frames=int(sum(v < 0.01 for v in vals)))
    for f in range(s["frame_start"] + 2, s["frame_end"] + 1):
        win = [diffs[g] for g in range(max(s["frame_start"] + 1, f - 6), min(s["frame_end"], f + 6) + 1) if g != f]
        med = float(np.median(win))
        if diffs[f] > max(3.0 * med, med + 2.0):
            flags.append((s["shot_id"], f, round(diffs[f], 2), round(med, 2)))
out = dict(flags=flags, per_shot=shots)
json.dump(out, open(os.path.join(C.P["metadata"], "animatic_motion_check.json"), "w"), indent=1)
print("FLAGS", len(flags), flags[:30])
