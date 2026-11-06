"""AMUL: OVER THE MOO · EPISODE 01: THE CALLING — project constants (no bpy).
World axes: +X = east, +Y = north, Z up, metres. One barn layout and one sun for every shot."""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {k: os.path.join(ROOT, v) for k, v in {"art": "art/moo_01", "meta": "metadata", "scenes": "scenes", "frames": "renders/frames",
                                            "stills": "renders/stills", "tests": "renders/tests", "audio": "audio",
                                            "stems": "audio/stems", "delivery": "delivery"}.items()}
FPS = 24
TOTAL_FRAMES = 720                      # brief frames 000-719 = Blender frames 1-720
RES_FINAL = (3840, 2160)
MOO_SCALE = 0.95                        # artwork design scale -> 0.90 m tall, 1.10 m nose to rump

# Sun: early sunrise, east-south-east, 9 degrees above the horizon.
SUN_AZIMUTH_DEG = 108.0                 # compass, clockwise from north
SUN_ELEVATION_DEG = 9.0
_az, _el = math.radians(SUN_AZIMUTH_DEG), math.radians(SUN_ELEVATION_DEG)
SUN_DIR = (math.sin(_az) * math.cos(_el), math.cos(_az) * math.cos(_el), math.sin(_el))   # unit vector toward the sun

# Barn (interior faces): west wall x=0 (entrance), east wall x=12 (double doors toward the sunrise)
BARN = dict(x0=0.0, x1=12.0, y0=-4.0, y1=4.0, eave=4.4, ridge=6.4, wall=0.14,
            entrance=dict(y0=-1.15, y1=1.15, h=2.7),                 # west entrance (open)
            doors=dict(y0=-1.8, y1=1.8, h=3.7, max_open_deg=40.0),    # east double doors, hinged at y = +-1.8, open inward
            windows=[(3.0, 2.5, 3.2), (9.0, 2.5, 3.2)])               # south wall windows: (x, z0, z1), 0.9 m wide
BLOCK = dict(x=6.0, y=0.0, w=0.45, d=0.35, h=0.25, slide_m=0.065)   # w across (y), d along push (x), h tall
PUDDLE = dict(x=-2.3, y=-0.92, rx=0.50, ry=0.50, depth=0.03)
MEADOW_MOO = (-14.0, 0.6)

# Shot table: brief frames (0-based, inclusive), lens, purpose. Blender frame = brief frame + 1.
SHOTS = [
    dict(id="S01", f0=0, f1=95, lens=24, name="EXT. DAIRY FARM - SUNRISE", view="rear"),
    dict(id="S02", f0=96, f1=167, lens=85, name="EXT. PUDDLE - CLOSE-UP", view="side"),
    dict(id="S03", f0=168, f1=263, lens=35, name="INT. TRAINING BARN - WIDE", view="rear"),
    dict(id="S04", f0=264, f1=359, lens=50, name="INT. BARN - FIRST ATTEMPT", view="side"),
    dict(id="S05", f0=360, f1=455, lens=50, name="INT. BARN - RECOVERY", view="side"),
    dict(id="S06", f0=456, f1=527, lens=50, name="INT. BARN - SECOND ATTEMPT", view="side"),
    dict(id="S07", f0=528, f1=575, lens=100, name="INT. BARN - BREAKTHROUGH DETAIL", view="side"),
    dict(id="S08", f0=576, f1=647, lens=85, name="INT. BARN - EMOTIONAL PAYOFF", view="q3"),
    dict(id="S09", f0=648, f1=695, lens=35, name="INT. BARN - MYSTERIOUS DOORS", view="rear"),
    dict(id="S10", f0=696, f1=719, lens=24, name="INT. BARN - FINAL STEP", view="rear"),
]


def bf(brief_frame):
    return brief_frame + 1


def shot_of(frame):
    for s in SHOTS:
        if bf(s["f0"]) <= frame <= bf(s["f1"]):
            return s
    return None
