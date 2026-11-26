"""Shot list for the 15-second cut (24 fps, 360 frames). Shared by render_cut.py (Blender) and sound.py (system Python).

Each shot plays a range of sim frames; "hold" shots repeat one sim frame while the camera moves.
Camera moves are eased from loc0/target0 to loc1/target1 over the shot.
"""

FPS = 24

SHOTS = [
    # name,        sim frames,          lens, f-stop, loc0,                 loc1,                 target0,               target1
    ("S1_Calm",     [1] * 48,            50, 4.0, (-0.55, -1.05, 0.10), (-0.12, -1.05, 0.10), (-0.35, -0.50, 0.01), (0.08, -0.50, 0.01)),
    ("S2_Drop",     list(range(1, 31)),  35, 5.6, (0.55, -1.35, 0.55),  (0.50, -1.25, 0.50),  (0.08, -0.12, 0.25),  (0.08, -0.12, 0.05)),
    ("S3_Impact",   list(range(22, 85)), 50, 2.8, (0.40, -0.82, 0.10),  (0.30, -0.84, 0.11),  (0.05, -0.13, 0.03),  (-0.25, -0.22, 0.03)),
    ("S4_Spread",   list(range(70, 171)), 24, 8.0, (0.10, -0.35, 2.00), (0.00, -0.25, 1.75),  (0.00, 0.00, 0.00),   (0.00, 0.02, 0.00)),
    ("S5_Chaos",    list(range(150, 216)), 28, 4.0, (1.35, -0.95, 0.18), (1.25, -0.55, 0.20), (0.20, 0.00, 0.02),   (0.00, 0.15, 0.02)),
    ("S6_Aftermath", list(range(205, 257)), 32, 5.6, (-0.20, -1.75, 0.65), (-0.10, -1.30, 0.42), (0.00, 0.00, 0.00), (-0.10, 0.00, 0.02)),
]


def ease(t):
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def film_frames():
    """Yields (film_frame, shot, index_in_shot, sim_frame, cam_loc, cam_target), film frames from 1."""
    n = 1
    for shot in SHOTS:
        name, sims, lens, fstop, l0, l1, t0, t1 = shot
        for i, s in enumerate(sims):
            t = ease(i / max(len(sims) - 1, 1))
            yield n, shot, i, s, lerp(l0, l1, t), lerp(t0, t1, t)
            n += 1


TOTAL = sum(len(s[1]) for s in SHOTS)
assert TOTAL == 15 * FPS, TOTAL
