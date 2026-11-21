"""OFFBRIEF S01E01 'THE PRODUCT IS MISSING' - single source of truth (room, cast, BOX_01 path, cameras, shots).
Metres; room centre (0,0,0); +X east, +Y north (presentation wall), +Z up. 'face' = body heading, degrees CCW from +X.
Master orientation looks north: windows (west) camera-left, glass partitions (east) camera-right."""

FPS, FRAME_START, FRAME_END = 24, 1, 720
ROOM = dict(width=9.0, depth=7.0, height=3.5)
TABLE = dict(center=(0.0, 0.5), width_x=1.25, length_y=3.6, top_z=0.75,
             legs=[(-0.48, -1.16), (-0.48, 2.0), (0.48, -1.16), (0.48, 2.0)])
SIDEBOARD = dict(center=(0.0, 3.255), size=(2.2, 0.45, 0.90))          # top at 0.90, front face at y = 3.03
MONITOR = dict(center=(0.0, 3.415, 1.62), width=1.88, height=1.06)       # 85" wall-mounted, display faces south
SEAT_TOP = 0.47
PENDANTS = [(0.0, -0.6), (0.0, 0.5), (0.0, 1.6), (2.4, 2.3), (-2.6, -1.8)]
K5600 = (1.0, 0.955, 0.905)
K3200 = (1.0, 0.70, 0.43)

T = 0.83   # wrist height over the 0.75 m table top (hand card clears the top)
CAST = {
    "NICO_01": dict(role="Creative", pos=(-1.05, -0.40), face=-12, H=1.0, G=1.0, pose="seated",
                    skin=(0.55, 0.38, 0.28), shirt=(0.20, 0.30, 0.46), sleeves="long", pants=(0.08, 0.10, 0.16),
                    hair=(0.07, 0.045, 0.03),
                    style=dict(hair="curly", mustache=True, aviators=True, tee=(0.92, 0.91, 0.88), pattern="denim"),
                    rest={"L": (-0.17, 0.45, T), "R": (0.19, 0.40, T)}),
    "SLOANE_01": dict(role="Strategy", pos=(-1.05, 1.00), face=6, H=0.96, G=0.9, pose="seated",
                      skin=(0.56, 0.39, 0.28), shirt=(0.02, 0.02, 0.022), sleeves="none", pants=(0.03, 0.03, 0.035),
                      hair=(0.10, 0.065, 0.04), style=dict(hair="updo", hoops=True, necklace=True),
                      rest={"L": (-0.14, 0.45, T), "R": (0.14, 0.45, T)}),
    "ELLIOT_01": dict(role="Accounts", pos=(1.45, 2.85), face=225, H=1.02, G=1.0, pose="standing",
                      skin=(0.62, 0.45, 0.35), shirt=(0.80, 0.84, 0.90), sleeves="long", pants=(0.42, 0.35, 0.25),
                      hair=(0.22, 0.13, 0.07),
                      style=dict(hair="curly", mustache=True, glasses=True, suspenders=True, tie=True, pattern="stripe"),
                      rest={"L": (-0.13, 0.30, 1.20), "R": (0.13, 0.30, 1.20)}),
    "VANTA_CLIENT": dict(role="Client (Vanta)", pos=(0.95, -0.82), face=165, H=1.0, G=1.1, pose="seated",
                         skin=(0.30, 0.19, 0.13), shirt=(0.07, 0.07, 0.085), sleeves="long", pants=(0.07, 0.07, 0.085),
                         hair=(0.02, 0.02, 0.02), style=dict(hair="short"),
                         rest={"L": (-0.18, 0.45, T), "R": (0.18, 0.45, T)}),
}
EMPTY_CHAIRS = [(1.05, 0.75, 180), (-1.05, 2.05, 0)]
ELLIOT_TABLET = dict(loc=(0.0, 0.33, 1.23), rot=(-50, 0, 0))

# --------------------------------------------------------------------------- BOX_01 path (root = sole of the sneakers)
# (frame, x, y, z). Screen plane y = 3.405 (1 cm in front of the display); sideboard top 0.90; table top 0.75.
BOX_SIZE_M = 0.40          # one art canvas (1000 px) = 0.40 m, constant from screen to table
BOX_PATH = [
    (313, -0.30, 3.405, 1.12), (330, -0.26, 3.405, 1.12), (346, -0.30, 3.405, 1.12), (360, -0.28, 3.405, 1.12),
    (364, -0.27, 3.330, 1.12),                    # first step through the screen plane
    (368, -0.25, 3.240, 1.06), (372, -0.23, 3.180, 0.90),      # drops onto the sideboard
    (376, -0.20, 3.150, 0.90), (380, -0.13, 3.110, 0.90), (384, -0.06, 3.075, 0.90), (388, 0.00, 3.060, 0.90),
    (390, 0.00, 3.060, 0.90),                     # anticipation crouch on the front edge
    (392, 0.01, 2.860, 1.03), (394, 0.02, 2.620, 1.08), (396, 0.03, 2.400, 1.02), (398, 0.04, 2.200, 0.86),
    (400, 0.05, 2.050, 0.75),                     # lands on the tabletop
    (720, 0.05, 2.050, 0.75),
]
BOX_DANCE = [(472, 0.02), (480, -0.02), (488, 0.02), (496, -0.02), (504, 0.02), (512, -0.02), (520, 0.0)]
# expressions: (frame, body, eyes, mouth); body in closed/open
BOX_FACE = [(313, "closed", "open", "open"), (402, "closed", "open", "smile"), (420, "open", "happy", "smile"),
            (450, "closed", "happy", "smile"), (470, "closed", "happy", "open"), (548, "closed", "open", "smile"),
            (600, "closed", "happy", "smile"), (664, "closed", "sad", "sad")]
# squash/stretch (frame, sx, sz) and arm angles (frame, left_deg, right_deg); 0 = hanging down, + = raised outward
BOX_SQUASH = [(313, 0.2, 0.2), (316, 1.12, 0.86), (319, 0.95, 1.06), (322, 1.0, 1.0),
              (370, 1.0, 1.0), (372, 1.1, 0.88), (375, 1.0, 1.0), (388, 1.0, 1.0), (390, 1.14, 0.82), (392, 0.9, 1.14),
              (398, 0.95, 1.06), (400, 1.18, 0.8), (403, 0.94, 1.07), (406, 1.0, 1.0),
              (664, 1.0, 1.0), (676, 1.08, 0.86)]
BOX_ARMS = [(313, 30, 30), (318, 120, 120), (326, 100, 140), (334, 120, 110), (342, 100, 140), (350, 120, 120),
            (360, 40, 40), (388, 60, 60), (392, 150, 150), (400, 110, 110), (406, 40, 40),
            (420, 70, 70), (450, 40, 40), (472, 120, 60), (480, 60, 120), (488, 120, 60), (496, 60, 120),
            (504, 120, 60), (512, 60, 120), (522, 40, 40), (552, 50, 50), (600, 90, 90), (624, 40, 40),
            (664, 40, 40), (676, 12, 12)]
BOX_STEPS = [(364, 368), (376, 388), (472, 520)]          # alternate legs while walking / dancing

# --------------------------------------------------------------------------- gaze: (frame, target, turn_frames, head_fraction)
SLOANE_BRIEF = "LOCAL:0.0,0.55,0.76"
ELLIOT_TAB = "LOCAL:0.0,0.33,1.23"
LOOKS = {
    "NICO_01": [(1, "ELLIOT_01"), (76, "SLOANE_01"), (124, "ELLIOT_01"), (198, "SLOANE_01", 6), (222, "VANTA_CLIENT", 6),
                (300, "SLOANE_01"), (314, "BOX", 8), (462, "VANTA_CLIENT", 8), (526, "BOX"), (550, "VANTA_CLIENT", 10),
                (604, "BOX"), (628, "SLOANE_01"), (690, "BOX")],
    "SLOANE_01": [(1, "ELLIOT_01"), (73, SLOANE_BRIEF, 6), (84, "ELLIOT_01", 8), (196, "ELLIOT_01"), (214, "NICO_01", 8),
                  (314, "BOX", 8), (470, "NICO_01"), (530, "BOX"), (550, "VANTA_CLIENT", 10), (604, "BOX")],
    "ELLIOT_01": [(1, "SLOANE_01"), (30, "NICO_01"), (56, "VANTA_CLIENT"), (76, "SLOANE_01"), (121, ELLIOT_TAB, 6),
                  (130, "SLOANE_01", 8), (224, "NICO_01"), (314, "BOX", 8), (470, "NICO_01"), (530, "BOX"),
                  (550, "VANTA_CLIENT", 10), (604, "BOX"), (628, "SLOANE_01"), (690, "BOX")],
    "VANTA_CLIENT": [(1, "ELLIOT_01"), (76, "SLOANE_01"), (124, "ELLIOT_01"), (196, "SLOANE_01"), (222, "NICO_01"),
                     (314, "BOX", 8), (470, "NICO_01"), (530, "BOX")],
}
TORSO = {   # (frame, lean_forward_deg, twist_left_deg)
    "NICO_01": [(1, -6, 0), (272, -6, 0), (282, 4, -6), (304, 4, -6), (316, -6, 0), (462, -6, 0), (472, 0, -4),
                (512, 0, -4), (524, -6, 0)],
    "SLOANE_01": [(1, 3, 0), (73, 3, 0), (80, 13, 0), (90, 6, 0), (314, 6, 0), (410, 6, 0), (420, 10, 8), (456, 6, 0),
                  (640, 6, 0), (652, 9, 6)],
    "ELLIOT_01": [(1, 2, 0), (314, 2, 0), (324, 0, 22), (400, 0, 8)],
    "VANTA_CLIENT": [(1, 2, 0), (548, 2, 0), (556, 6, 0), (600, 6, 0), (610, 2, 0)],
}
HANDS = {
    "NICO_01": {"R": [(1, (0.19, 0.40, T)), (272, (0.19, 0.40, T)), (280, (0.20, 0.42, 0.92)), (288, (0.25, 0.50, 1.02)),
                      (300, (0.25, 0.50, 1.02)), (312, (0.19, 0.40, T)), (466, (0.19, 0.40, T)), (476, (0.21, 0.45, 0.90)),
                      (490, (0.24, 0.50, 0.96)), (508, (0.19, 0.40, T))],
                "L": [(1, (-0.17, 0.45, T))]},
    "SLOANE_01": {"R": [(1, (0.14, 0.45, T))], "L": [(1, (-0.14, 0.45, T))]},
    "ELLIOT_01": {"R": [(1, (0.13, 0.30, 1.20)), (16, (0.13, 0.30, 1.20)), (24, (0.30, 0.36, 1.32)), (40, (0.29, 0.37, 1.30)),
                        (50, (0.13, 0.30, 1.20))],
                  "L": [(1, (-0.13, 0.30, 1.20))]},
    "VANTA_CLIENT": {"R": [(1, (0.18, 0.45, T))], "L": [(1, (-0.18, 0.45, T))]},
}
HAND_NOISE = {"ELLIOT_01": [("R", 121, 130, 0.02, 2.0)]}

# --------------------------------------------------------------------------- cameras and shots
# Six cameras (brief hierarchy). A camera may hold several set-ups; each set-up is keyed (constant) at its shot start.
CAMERAS = {"CAM_MASTER": dict(lens=35, fstop=5.6), "CAM_SLOANE": dict(lens=50, fstop=2.8),
           "CAM_ELLIOT": dict(lens=50, fstop=2.8), "CAM_NICO": dict(lens=50, fstop=2.8),
           "CAM_BOX": dict(lens=65, fstop=2.8), "CAM_TRANSITION": dict(lens=35, fstop=4.0)}
SHOTS = [
    dict(n=1, start=1, end=72, cam="CAM_MASTER", setup="A", pos=(-0.30, -3.15, 1.45), aim=(0.15, 2.4, 1.25),
         focus="ELLIOT_01", beat="Master wide: Elliot at the screen with his tablet; Nico and Sloane screen-left, client foreground right.",
         dialogue=[("ELLIOT_01", "Good news. We got the brief.", 12, 58)]),
    dict(n=2, start=73, end=120, cam="CAM_SLOANE", setup="A", pos=(0.40, 0.00, 1.22), aim="SLOANE_01", aim_dz=-0.10,
         focus="SLOANE_01", beat="Sloane leans toward the table, studies the brief, looks up at Elliot.",
         dialogue=[("SLOANE_01", "Where's the product?", 88, 112)]),
    dict(n=3, start=121, end=192, cam="CAM_ELLIOT", setup="A", pos=(0.78, 0.97, 1.50), aim="ELLIOT_01", aim_dz=-0.14,
         focus="ELLIOT_01", beat="Elliot glances at the tablet, then delivers with professional optimism.",
         dialogue=[("ELLIOT_01", "They haven't invented it yet.", 134, 178)]),
    dict(n=4, start=193, end=240, cam="CAM_SLOANE", setup="B", pos=(0.45, -1.95, 1.25), aim=(-1.05, 0.25, 1.12),
         focus="SLOANE_01", beat="Two-shot across the table: Sloane turns to Nico; Nico answers toward the client.",
         dialogue=[("SLOANE_01", "Then what are we selling?", 196, 214), ("NICO_01", "Anticipation.", 224, 238)]),
    dict(n=5, start=241, end=312, cam="CAM_NICO", setup="A", pos=(0.33, -1.56, 1.22), aim="NICO_01", aim_dz=-0.10,
         focus="NICO_01", beat="Nico, relaxed; one deliberate open-hand gesture on 'possibilities'.",
         dialogue=[("NICO_01", "People don't buy products. They buy possibilities.", 248, 306)]),
    dict(n=6, start=313, end=360, cam="CAM_BOX", setup="A", pos=(0.22, 0.95, 1.32), aim=(-0.27, 3.4, 1.30),
         focus="BOX", beat="The slide changes: BOX_01 pops onto the illustration panel and waves.", dialogue=[]),
    dict(n=7, start=361, end=408, cam="CAM_TRANSITION", setup="A", pos=(0.85, 0.30, 1.30), aim=(-0.08, 2.75, 1.02),
         focus="BOX", beat="BOX_01 steps through the screen plane onto the sideboard, leaps, lands on the tabletop.",
         dialogue=[]),
    dict(n=8, start=409, end=456, cam="CAM_BOX", setup="B", pos=(0.25, 0.35, 1.02), aim=(0.05, 2.05, 0.93),
         focus="BOX", beat="BOX_01 opens its flaps: empty. Sloane (off-screen, left) delivers the line.",
         dialogue=[("SLOANE_01", "There's literally nothing inside.", 418, 450)]),
    dict(n=9, start=457, end=624, cam="CAM_MASTER", setup="B", pos=(-0.20, -2.70, 1.40), aim=(-0.55, 2.29, 1.10),
         focus="BOX", beat="Nico foreground-left, BOX_01 dancing on the table, Elliot background-right. Client is off-screen right.",
         dialogue=[("NICO_01", "Exactly. Unlimited potential.", 470, 520),
                   ("VANTA_CLIENT", "I love it. Can we sell the box?", 548, 600)]),
    dict(n=10, start=625, end=720, cam="CAM_SLOANE", setup="C", pos=(0.30, -0.90, 1.12), aim=(-0.48, 1.55, 1.00),
         focus="SLOANE_01", beat="Sloane foreground-left, quiet and precise; BOX_01 deflates into a sad slump.",
         dialogue=[("SLOANE_01", "That's not the product.", 656, 688)]),
]
