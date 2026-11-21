"""Single source of truth for OFFBRIEF EP01: room, cast blocking, performance keys and the ten shots.
Coordinates: metres, room centre (0,0,0); +X east, +Y north, +Z up. Angles in degrees.
'face' is the direction an actor's body faces, measured counter-clockwise from +X (east)."""

FPS, FRAME_START, FRAME_END = 24, 1, 720
ROOM = dict(width=9.0, depth=7.0, height=3.5)
TABLE = dict(center=(0.0, -0.3), width_x=1.25, length_y=3.6, top_z=0.75,
             legs=[(-0.48, -1.7), (-0.48, 1.1), (0.48, -1.7), (0.48, 1.1)])
MONITOR = dict(center=(0.0, 3.38, 1.65), width=2.8, height=1.575)
SEAT_TOP = 0.47
PENDANTS = [(0.0, -1.45), (0.0, -0.3), (0.0, 0.85), (-1.9, 2.0), (2.6, -1.6)]
K5600 = (1.0, 0.955, 0.905)
K3200 = (1.0, 0.70, 0.43)

# --------------------------------------------------------------------------- cast
# H = height factor, G = girth factor. 'rest' = IK wrist targets in actor-local metres (+Y forward, +X actor's right).
T = 0.80        # wrist height over the 0.75 m table top (forearm rests on the table)
CAST = {
    "JASON_01": dict(role="Creative Director", pos=(-1.05, 0.55), face=-8, H=1.03, G=1.0,
                     skin=(0.55, 0.40, 0.30), shirt=(0.10, 0.10, 0.11), sleeves="long", pants=(0.06, 0.06, 0.07),
                     hair=(0.04, 0.035, 0.03), style=dict(hair="short", stubble=True),
                     rest={"L": (-0.17, 0.45, T), "R": (0.17, 0.45, T)}),
    "LUCIA_01": dict(role="Head of Strategy", pos=(-1.05, -1.10), face=4, H=0.96, G=0.9,
                     skin=(0.50, 0.33, 0.22), shirt=(0.025, 0.025, 0.03), sleeves="long", pants=(0.03, 0.03, 0.035),
                     hair=(0.045, 0.03, 0.025), style=dict(hair="curly_pony", hoops=True),
                     rest={"L": (-0.15, 0.45, T), "R": (0.15, 0.45, T)}),
    "BOOBIE_IKE_01": dict(role="Founder / CEO", pos=(1.05, 0.65), face=195, H=1.05, G=1.38, belly=1.35,
                          skin=(0.17, 0.095, 0.06), shirt=(0.26, 0.07, 0.36), sleeves="short", pants=(0.05, 0.05, 0.06),
                          hair=(0.02, 0.02, 0.02), style=dict(hair="bald", beard=(0.02, 0.02, 0.02), aviators=True,
                                                              chains=True, pattern="gold_paisley"),
                          rest={"L": (-0.22, 0.42, T), "R": (0.22, 0.42, T)}),
    "BRIAN_01": dict(role="Head of Accounts", pos=(1.05, -1.15), face=190, H=1.02, G=1.2, belly=1.2,
                     skin=(0.66, 0.40, 0.31), shirt=(0.47, 0.55, 0.43), sleeves="short", pants=(0.20, 0.18, 0.15),
                     hair=(0.55, 0.53, 0.50), style=dict(hair="cap", beard=(0.58, 0.56, 0.53), chains=True,
                                                         pattern="floral"),
                     rest={"L": (-0.2, 0.44, T), "R": (0.2, 0.46, T + 0.01)}),
    "BAE_LUXE_01": dict(role="Head of Culture & Social", pos=(0.0, -2.25), face=25, H=0.95, G=0.9,
                        skin=(0.45, 0.29, 0.19), shirt=(0.86, 0.36, 0.55), sleeves="long", pants=(0.05, 0.05, 0.06),
                        hair=(0.03, 0.022, 0.018), style=dict(hair="long_curly", hoops=True, pattern="varsity"),
                        rest={"L": (-0.16, 0.45, T), "R": (0.16, 0.45, T)}),
    "LORI_01": dict(role="Head of Production", pos=(-1.65, 1.75), face=-45, H=0.95, G=0.92,
                    skin=(0.62, 0.45, 0.33), shirt=(0.10, 0.13, 0.20), sleeves="long", pants=(0.12, 0.14, 0.20),
                    hair=(0.60, 0.48, 0.28), style=dict(hair="bun", hoops=True), head_follow=0.9,
                    rest={"L": (-0.10, 0.24, 0.69), "R": (0.05, 0.30, 0.69)}),
}
LORI_NOTEBOOK = dict(loc=(-0.01, 0.31, 0.64), rot=(6, 0, 8))

# --------------------------------------------------------------------------- gaze (frame, target, turn_frames, head_fraction)
# target: another actor (looks at their eyes), "SCREEN", or "LOCAL:x,y,z" in the actor's own space.
# head_fraction < 1 turns the head only part-way while the eyes go all the way ("barely looks up").
LORI_BOOK = "LOCAL:0.0,0.34,0.64"
JASON_TABLE = "LOCAL:0.0,0.62,0.76"
LOOKS = {
    "BRIAN_01": [(1, "LUCIA_01"), (64, "BOOBIE_IKE_01", 8), (148, "BAE_LUXE_01"), (222, "LORI_01"),
                 (296, "SCREEN", 10), (362, "JASON_01", 6), (440, "LUCIA_01"), (468, "SCREEN", 10),
                 (562, "LUCIA_01"), (582, "BOOBIE_IKE_01"), (670, "LORI_01")],
    "BOOBIE_IKE_01": [(1, "BRIAN_01"), (74, "JASON_01", 8), (148, "BAE_LUXE_01"), (222, "LORI_01"),
                      (294, "JASON_01"), (318, "SCREEN", 10), (364, "BRIAN_01"), (406, "JASON_01"),
                      (440, "LUCIA_01"), (464, "SCREEN", 10), (578, "LUCIA_01", 10), (668, "LORI_01")],
    "BAE_LUXE_01": [(1, "BRIAN_01"), (76, "BOOBIE_IKE_01"), (146, "BRIAN_01", 8), (224, "LORI_01"),
                    (296, "JASON_01"), (320, "SCREEN", 10), (364, "BRIAN_01"), (404, "JASON_01"),
                    (440, "LUCIA_01"), (464, "SCREEN", 10), (548, "LUCIA_01"), (580, "BOOBIE_IKE_01"),
                    (670, "LORI_01")],
    "LORI_01": [(1, LORI_BOOK), (228, "BAE_LUXE_01", 10, 0.3), (264, LORI_BOOK, 10),
                (366, "BRIAN_01", 8, 0.4), (392, LORI_BOOK, 10), (664, "BOOBIE_IKE_01", 9)],
    "JASON_01": [(1, "BRIAN_01"), (76, "BOOBIE_IKE_01"), (150, "BAE_LUXE_01"), (224, "LORI_01"),
                 (289, "BOOBIE_IKE_01", 6), (302, "SCREEN", 12), (346, JASON_TABLE, 12),
                 (398, "BRIAN_01", 8, 0.25), (432, "SCREEN", 12), (590, "BOOBIE_IKE_01"), (672, "LORI_01")],
    "LUCIA_01": [(1, "BRIAN_01"), (76, "BOOBIE_IKE_01"), (150, "BAE_LUXE_01"), (224, "LORI_01"),
                 (296, "JASON_01"), (364, "BRIAN_01"), (404, "JASON_01"), (426, "BRIAN_01", 7),
                 (446, "SCREEN", 10), (534, "BRIAN_01", 8), (580, "BOOBIE_IKE_01"), (672, "LORI_01")],
}

# --------------------------------------------------------------------------- torso (frame, lean_fwd_deg, twist_left_deg)
TORSO = {
    "BRIAN_01": [(1, 9, 0), (58, 9, 0), (78, 3, 0), (360, 3, 0), (366, 9, -16), (396, 9, -16), (420, 4, -6),
                 (500, 4, -6), (512, 7, 4), (560, 7, 4), (580, 3, 0)],
    "BOOBIE_IKE_01": [(1, 0, 0), (76, 0, 0), (88, -9, 0), (582, -9, 0), (596, 3, 0)],
    "BAE_LUXE_01": [(1, -5, 0), (150, -5, 0), (160, 3, 6), (200, 3, 6), (214, -5, 0)],
    "LORI_01": [(1, 10, 0), (226, 10, 0), (236, 7, 0), (262, 7, 0), (272, 10, 0), (660, 10, 0), (670, 5, 0)],
    "JASON_01": [(1, 2, 0), (300, 2, 0), (312, 1, 14), (344, 1, 14), (356, 3, 0)],
    "LUCIA_01": [(1, 1, 0), (444, 1, 0), (456, 0, 12), (528, 0, 12), (540, 1, 0)],
}

# --------------------------------------------------------------------------- hands (IK wrist targets, actor-local)
R_, L_ = CAST["BRIAN_01"]["rest"]["R"], CAST["BRIAN_01"]["rest"]["L"]
HANDS = {
    "BRIAN_01": {
        "R": [(1, (0.14, 0.48, 0.90)), (8, (0.13, 0.50, 0.97)), (18, (0.12, 0.52, 0.92)), (28, (0.13, 0.50, 0.98)),
              (40, (0.12, 0.52, 0.93)), (52, (0.13, 0.50, 0.97)), (62, (0.14, 0.48, 0.90)), (76, R_),
              (362, R_), (368, (0.16, 0.46, 0.98)), (376, (0.14, 0.50, 0.95)), (386, (0.16, 0.47, 0.99)),
              (398, (0.17, 0.46, 0.92)), (410, R_)],
        "L": [(1, L_), (362, L_), (368, (-0.24, 0.40, 0.97)), (376, (-0.22, 0.44, 0.94)), (386, (-0.24, 0.41, 0.98)),
              (398, (-0.22, 0.42, 0.90)), (410, L_)],
    },
    "BOOBIE_IKE_01": {
        "R": [(1, (0.22, 0.42, 0.80)), (80, (0.22, 0.42, 0.80)), (90, (0.24, 0.30, 0.76)), (96, (0.22, 0.38, 1.02)),
              (104, (0.21, 0.44, 0.95)), (118, (0.21, 0.44, 0.95)), (132, (0.24, 0.30, 0.76)),
              (582, (0.24, 0.30, 0.76)), (594, (0.10, 0.18, 1.08)), (606, (0.09, 0.19, 1.10)), (622, (0.11, 0.20, 1.06)),
              (640, (0.24, 0.30, 0.76))],
        "L": [(1, (-0.22, 0.42, 0.80)), (80, (-0.22, 0.42, 0.80)), (92, (-0.25, 0.30, 0.76))],
    },
    "BAE_LUXE_01": {
        "R": [(1, (0.16, 0.45, 0.80)), (154, (0.16, 0.45, 0.80)), (164, (0.14, 0.36, 1.00)), (196, (0.14, 0.37, 0.99)),
              (208, (0.16, 0.45, 0.80))],
        "L": [(1, (-0.16, 0.45, 0.80))],
    },
    "LUCIA_01": {
        "R": [(1, (0.15, 0.45, 0.80)), (456, (0.15, 0.45, 0.80)), (464, (0.14, 0.42, 0.86)), (478, (0.14, 0.43, 0.85)),
              (490, (0.15, 0.45, 0.80))],
        "L": [(1, (-0.15, 0.45, 0.80))],
    },
    "JASON_01": {"R": [(1, (0.17, 0.45, 0.80))], "L": [(1, (-0.17, 0.45, 0.80))]},
    "LORI_01": {"R": [(1, (0.05, 0.30, 0.69)), (226, (0.05, 0.30, 0.69)), (232, (0.06, 0.27, 0.70)),
                      (262, (0.06, 0.27, 0.70)), (268, (0.05, 0.30, 0.69)), (664, (0.05, 0.30, 0.69)),
                      (670, (0.06, 0.27, 0.70))],
                "L": [(1, (-0.10, 0.24, 0.69))]},
}
# writing / finger-flick micro motion: (side, start, end, strength_m, scale_frames)
HAND_NOISE = {
    "LORI_01": [("R", 1, 226, 0.03, 3.0), ("R", 270, 360, 0.03, 3.0), ("R", 400, 664, 0.03, 3.0)],
    "BAE_LUXE_01": [("R", 168, 194, 0.035, 2.5)],
}
# Boobie pulls his sunglasses down his nose: glasses bone location (x, forward, up) in head space
BOOBIE_GLASSES = [(1, (0, 0, 0)), (597, (0, 0, 0)), (606, (0, 0.012, -0.026))]

# --------------------------------------------------------------------------- shots
SHOTS = [
    dict(n=1, start=1, end=72, cam="CAM_01", lens=50, fstop=2.8, subject="BRIAN", framing="Medium close-up",
         pos=(-0.60, -1.90, 1.22), aim="BRIAN_01", aim_dz=-0.10, focus="BRIAN_01",
         dialogue=[("BRIAN_01", "Client wants the ketchup bottle in every shot.", 6, 60)],
         notes="Brian leans forward holding the client brief; quick, forced enthusiasm; eyebrow-lift beat on 'every'. "
               "Camera on a table-top tripod at the SW corner; Brian looks screen-left at Lucia."),
    dict(n=2, start=73, end=144, cam="CAM_02", lens=50, fstop=2.8, subject="BOOBIE", framing="Medium close-up",
         pos=(-0.42, -0.22, 1.25), aim="BOOBIE_IKE_01", aim_dz=-0.12, focus="BOOBIE_IKE_01",
         dialogue=[("BOOBIE_IKE_01", "Make it gold.", 94, 118)],
         notes="Boobie leans back, one decisive right-hand chop on 'gold'; minimal head movement. Looks screen-left at Jason."),
    dict(n=3, start=145, end=216, cam="CAM_03", lens=50, fstop=2.8, subject="BAE_LUXE", framing="Medium close-up",
         pos=(1.62, -2.42, 1.20), aim="BAE_LUXE_01", aim_dz=-0.10, focus="BAE_LUXE_01",
         dialogue=[("BAE_LUXE_01", "Get an influencer to lick it.", 158, 200)],
         notes="Relaxed, matter-of-fact pitch to Brian; right hand rises with one small finger flick."),
    dict(n=4, start=217, end=288, cam="CAM_04", lens=85, fstop=2.8, subject="LORI", framing="Tight close-up",
         pos=(-0.12, 1.56, 1.17), aim="LORI_01", aim_dz=-0.03, focus="LORI_01", handheld=True,
         dialogue=[("LORI_01", "Please don't.", 236, 254)],
         notes="Lori barely looks up from her notebook: eyes up to Bae-Luxe, head only 30%. Controlled pause after. "
               "Restrained handheld reaction."),
    dict(n=5, start=289, end=360, cam="CAM_05", lens=50, fstop=2.8, subject="JASON", framing="Medium close-up",
         pos=(0.76, 0.04, 1.27), aim="JASON_01", aim_dz=-0.10, focus="JASON_01", push=0.15,
         dialogue=[("JASON_01", "Remove the bottle.", 314, 338)],
         notes="Jason turns from Boobie to the presentation screen; still shoulders, quiet conviction. "
               "The only camera move: 0.15 m push-in over 3 s (0.05 m/s)."),
    dict(n=6, start=361, end=432, cam="CAM_06", lens=35, fstop=4.0, subject="BRIAN_JASON", framing="Two-shot across the table",
         pos=(1.48, -2.15, 1.34), aim=(-0.20, -0.05, 1.05), focus="JASON_01",
         dialogue=[("BRIAN_01", "It's a ketchup ad!", 364, 392), ("JASON_01", "Exactly.", 408, 424)],
         notes="Brian (foreground, screen-right) turns toward Jason with open hands; Jason (screen-left, across the "
               "table) barely reacts: eyes up, 25% head turn. Locked off."),
    dict(n=7, start=433, end=504, cam="CAM_07", lens=50, fstop=2.8, subject="LUCIA", framing="Medium close-up",
         pos=(0.45, -1.58, 1.24), aim="LUCIA_01", aim_dz=-0.10, focus="LUCIA_01",
         dialogue=[("LUCIA_01", "What's missing?", 458, 482)],
         notes="Lucia looks from Brian to the presentation monitor; calm, curious, small controlled head turn."),
    dict(n=8, start=505, end=576, cam="CAM_08", lens=35, fstop=4.0, subject="SCREEN_BRIAN", framing="Over-the-shoulder",
         pos=(0.72, -2.36, 1.40), aim=(0.05, 3.3, 1.45), focus="SCREEN",
         dialogue=[("BRIAN_01", "Ketchup.", 516, 530), ("LUCIA_01", "Now you want it.", 540, 566)],
         notes="Over Brian's right shoulder onto the static burger photograph (no bottle, no sauce). Brian studies the "
               "screen; Lucia's line is off-screen, she stays seated."),
    dict(n=9, start=577, end=648, cam="CAM_09", lens=50, fstop=2.8, subject="BOOBIE", framing="Medium close-up",
         pos=(0.50, -0.95, 1.24), aim="BOOBIE_IKE_01", aim_dz=-0.10, focus="BOOBIE_IKE_01", handheld=True,
         dialogue=[("BOOBIE_IKE_01", "We're charging them NOT to show it?", 586, 636)],
         notes="Boobie leans in, pulls his sunglasses down his nose, looks across the table at Lucia. Confused but "
               "intrigued. Restrained handheld reaction."),
    dict(n=10, start=649, end=720, cam="CAM_10", lens=85, fstop=2.8, subject="LORI", framing="Tight close-up",
         pos=(-0.26, 1.00, 1.16), aim="LORI_01", aim_dz=-0.03, focus="LORI_01",
         dialogue=[("LORI_01", "First profitable idea this week.", 674, 706)],
         notes="Lori finishes writing, looks up briefly at Boobie (almost to lens). Completely deadpan. Hold to the "
               "last frame; hard cut to black."),
]
