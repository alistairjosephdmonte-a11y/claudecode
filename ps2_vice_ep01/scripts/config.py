"""PLAYSTATION x GTA VI · EP 01 · THE FIRST HIT — block animatic constants (no bpy).
World axes: +Y = toward the CRT (front wall), +X = room east (desk side), Z up, metres.
The gamer faces +Y. Brief frames 001-480 are Blender frames 1-480 (no offset)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {k: os.path.join(ROOT, v) for k, v in {"tex": "textures", "meta": "metadata", "scenes": "scenes", "frames": "renders/frames",
                                            "shots": "renders/shots", "stills": "renders/stills", "tests": "renders/tests",
                                            "audio": "audio", "delivery": "delivery"}.items()}
FPS = 24
TOTAL_FRAMES = 480
RES = (1920, 1080)

PAL = dict(pink="#F54BA5", cyan="#22C9CE", orange="#FFB35C", purple="#8656A8", navy="#172C47")


def rgb(h, a=1.0):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s) + (a,)


# ROOM_01 (interior faces). The front wall (y=2.0) is two hinged leaves either side of the CRT that swing out onto
# WORLD_01: Ocean Drive runs along +Y beyond it. Left opening (x -3.0..-0.70): CAR_01. Right opening (0.70..2.0): TOMMY_01.
ROOM = dict(x0=-3.0, x1=2.0, y0=-2.0, y1=2.0, h=2.6, wall=0.12)
CABINET = dict(x=0.0, y=1.70, w=1.40, d=0.55, h=0.62, shelf_z=0.30)     # TV stand: CRT and PS2 side by side on top
CRT = dict(w=0.70, d=0.45, h=0.54, screen=(0.54, 0.405), y=1.76)          # 4:3 tube TV set back on the cabinet top
PS2 = dict(x=0.52, z=0.62, w=0.301, d=0.182, h=0.078, front_y=1.45, tray_out=0.135)   # on the cabinet top, right of the CRT
DISC = dict(r=0.060, hole_r=0.0075, t=0.0012)                             # 120 mm DVD
SEAT = dict(x=0.0, y=0.70, h=0.44, r=0.26)                                # gamer's pouf
BED = dict(x=0.0, y=-1.45, w=2.0, d=1.0, h=0.45)
DESK = dict(x=1.68, y=-0.55, w=0.6, d=1.1, h=0.74)                       # against the east wall, behind-right of the gamer
TOMMY_START = (1.28, 3.35)                                                # on the street, in the right opening
TOMMY_MARK = (0.82, 1.02)                                                 # where TOMMY_01 stops, beside the cabinet
CAR = dict(x=-1.85, len=4.3, w=1.9, h=1.12, wheel_r=0.33, start_front_y=13.0, stop_front_y=0.85)
GAMER_H, TOMMY_H = 1.70, 1.85

SHOTS = [
    dict(id="S01", f0=1, f1=48, lens=35, name="Gamer, CRT and PS2 geography", motion="25 cm dolly-in"),
    dict(id="S02", f0=49, f1=96, lens=85, name="DISC_01 held at the rim", motion="15 deg arc around the disc"),
    dict(id="S03", f0=97, f1=144, lens=100, name="Disc placed in the tray, tray closes", motion="locked off, console height"),
    dict(id="S04", f0=145, f1=192, lens=50, name="CRT powers up, title art", motion="slow 10 cm push"),
    dict(id="S05", f0=193, f1=240, lens=24, name="Portal: Ocean Drive opens, car rolls in", motion="locked off behind gamer, slight rise"),
    dict(id="S06", f0=241, f1=288, lens=35, name="TOMMY_01 steps into the room", motion="low angle, 12 deg tilt up"),
    dict(id="S07", f0=289, f1=336, lens=50, name="\"Welcome to Vice City\"", motion="slow 8 cm push"),
    dict(id="S08", f0=337, f1=384, lens=50, name="Controller handoff, \"bigger TV\"", motion="locked off"),
    dict(id="S09", f0=385, f1=432, lens=28, name="Rear shoulder: car cruises away", motion="slow 15 cm push"),
    dict(id="S10", f0=433, f1=480, lens=35, name="Pull-out to skyline, slate", motion="pull-out and rise, then slate"),
]
# TOMMY_01 dialogue (temp espeak-ng guide in audio/dialogue/): start frame, length in frames (voiced), syllables
DIALOGUE = [dict(id="tommy_01", text="Welcome to Vice City.", f0=298, frames=34, syll=6),
            dict(id="tommy_02", text="You're gonna need a bigger TV.", f0=363, frames=33, syll=8)]
SLATE_F = 469                     # slate THE JOURNEY CONTINUES holds 469-480


def shot_of(f):
    return next(s for s in SHOTS if s["f0"] <= f <= s["f1"])
