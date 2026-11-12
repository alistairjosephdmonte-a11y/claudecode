"""THE LAST JOB · EP01 · THE WRONG BAG — block previs constants (no bpy).
World: +Y = the car's heading when parked, +X = passenger side, Z up, metres.
Everything inside CAR_01 is authored in car-local coordinates (parented to CAR_01_BODY), so it rides the brake dive.
Frames 0-299 at 30 fps; shots are [start, end) as in the brief."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {k: os.path.join(ROOT, v) for k, v in {"tex": "textures", "meta": "metadata", "scenes": "scenes", "frames": "renders/frames",
                                            "tests": "renders/tests", "audio": "audio", "delivery": "delivery"}.items()}
FPS = 30
F0, F1 = 0, 299
RES = (1920, 1080)

PAL = dict(pink="#F34AA5", magenta="#C54B9D", purple="#7659B8", blue="#4074C8", peach="#FFAD72", plum="#21162D")


def rgb(h, a=1.0):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s) + (a,)


# CAR_01: dark two-door muscle car, left-hand drive. Car-local origin = ground, centre of the wheelbase.
CAR = dict(len=4.85, w=1.90, h=1.34, wheel_r=0.34, wheelbase=2.75, track=1.56,
           roof_z=1.30, floor_z=0.18, seat_z=0.27, seat_y=-0.30, driver_x=-0.37, pass_x=0.37,
           wheel_c=(-0.37, 0.24, 0.84), wheel_rad=0.19, dash_z=0.84,
           brake_start_y=-22.0, stop_y=0.0, brake_f=(0, 24))        # world Y of the car root over S01
JASON_H, LUCIA_H = 1.85, 1.70

# BAG_01 on Lucia's lap, across her thighs (long axis = car X). Bag-local origin = bottom centre.
BAG = dict(L=0.62, W=0.34, H=0.30, x=0.37, y=0.0, z=0.50, zip_x0=-0.24, zip_x1=0.26)
ZIP = dict(insert=(94, 116), start=-0.24, after_insert=-0.09, full=0.25, full_f=(122, 131), flaps_f=(132, 144),
           flap_deg=dict(front=150, back=70))     # front flap folds down toward the dash; back flap stands up toward Lucia
# Products (real-world dimensions, metres): PS5 disc edition lies flat in the foam
PS5 = dict(h=0.390, w=0.104, d=0.260)
DUALSENSE = dict(w=0.160, d=0.106, h=0.066)
CASE = dict(w=0.135, h=0.170, t=0.014)
TAG = dict(w=0.095, h=0.050, text="PROPERTY OF VICE CITY POLICE", pinch=212, flip=(213, 221), legible=(220, 239))

# LOCATION_01: petrol station; canopy over the pump island on the driver side
CANOPY = dict(x0=-6.0, x1=4.0, y0=-5.0, y1=6.0, z=4.6, t=0.45)
PUMPS = dict(x=-2.05, ys=(-2.0, 2.2))
POLICE = (-38.0, 52.0)                       # distant police car with flashing bar
HELI = dict(start=(-10.0, 44.0, 20.0), end=(-4.0, 30.0, 16.0))     # approach clears the canopy pillars
BEAM = dict(f=(246, 264), face=(274, 292))

SHOTS = [
    dict(id="SHOT_01", cam="CAM_01", f0=0, f1=30, lens=35, desc="EXT. car brakes and settles under the canopy", motion="low tracking, stops with the car"),
    dict(id="SHOT_02", cam="CAM_02", f0=30, f1=60, lens=65, desc="INT. Jason CU, glance to passenger", motion="locked off"),
    dict(id="SHOT_03", cam="CAM_03", f0=60, f1=90, lens=65, desc="INT. Lucia CU, raises duffel 8 cm", motion="locked off"),
    dict(id="SHOT_04", cam="CAM_04", f0=90, f1=120, lens=85, desc="INS. Jason unzips 15 cm left-to-right", motion="locked off"),
    dict(id="SHOT_05", cam="CAM_05", f0=120, f1=150, lens=50, desc="INS. overhead bag reveal", motion="slight push-in"),
    dict(id="SHOT_06", cam="CAM_06", f0=150, f1=180, lens=85, desc="INT. Jason reaction", motion="locked off"),
    dict(id="SHOT_07", cam="CAM_07", f0=180, f1=210, lens=85, desc="INT. Lucia CU, half-smile", motion="locked off"),
    dict(id="SHOT_08", cam="CAM_08", f0=210, f1=240, lens=100, desc="INS. macro: Lucia flips the tag", motion="locked off"),
    dict(id="SHOT_09", cam="CAM_09", f0=240, f1=270, lens=35, desc="EXT. helicopter searchlight finds the windshield", motion="locked off"),
    dict(id="SHOT_10", cam="CAM_10", f0=270, f1=300, lens=85, desc="INT. Jason CU, light crosses face", motion="locked off"),
]
DIALOGUE = [dict(id="JASON_01", who="JASON_01", text="We got the money?", f0=32, f1=57),
            dict(id="LUCIA_01", who="LUCIA_01", text="We got the bag.", f0=62, f1=87),
            dict(id="JASON_02", who="JASON_01", text="What the hell?", f0=153, f1=176),
            dict(id="LUCIA_02", who="LUCIA_01", text="Wrong bag.", f0=183, f1=205),
            dict(id="JASON_03", who="JASON_01", text="Oh, we're dead.", f0=273, f1=297)]


def shot_of(f):
    return next(s for s in SHOTS if s["f0"] <= f < s["f1"])
