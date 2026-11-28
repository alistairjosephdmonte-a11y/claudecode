"""Expands the animatic's unique frames to the full 1-360 sequence (system python3).

    python3 scripts/hold_fill.py <raw_dir> <out_dir>

Locked shots with constant lighting were rendered once; every missing frame repeats the latest earlier rendered
frame (identical to rendering it: fixed Cycles seed, nothing moves). Frames 277-360 use the composited slate."""
import os
import shutil
import sys

raw, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
src = None
for f in range(1, 361):
    p = os.path.join(raw, "frame_%04d.png" % f)
    if f == 277:
        p = os.path.join(raw, "frame_0277_slate.png")
    if os.path.exists(p) and f <= 277:
        src = p
    shutil.copyfile(src, os.path.join(out, "frame_%04d.png" % f))
print("HOLD_FILL", out)
