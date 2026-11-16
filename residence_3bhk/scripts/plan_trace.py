"""Traced geometry for the 3-bedroom apartment plan (reference/floor_plan.jpg, 1600 x 839 px).

Every coordinate below was read off the drawing in image pixels (x right, y down) and is converted to
metres by a scale fitted to the dimensioned rooms (fit_scale). Nothing is derived from the room schedule
alone: the schedule is only used to fit the scale and to check the trace afterwards.

Wall kinds
  core  structural walls drawn solid black on the plan; traced as rectangles at their drawn thickness
  ext   exterior walls drawn as a thin line / glazing line; traced as the room-side face plus the side the
        wall thickens towards, thickness = PARAMS["ext_t"]; corners=(start, end) carries the wall through a
        convex outside corner
  int   interior partitions drawn as thin grey lines; traced as the centre line, thickness = PARAMS["int_t"]
Openings are (along_from_px, along_to_px, kind, extra) on their wall."""

import math

IMG = (1600, 839)
ORIGIN_PX = (707.0, 617.0)          # inner south-west corner of the master bedroom -> Blender (0, 0)

PARAMS = dict(
    ext_t=0.23,            # provisional exterior wall thickness (m)
    int_t=0.115,           # provisional interior wall thickness (m)
    wall_h=3.0,            # provisional floor-to-ceiling height (m)
    door_h=2.1,
    entry_door_h=2.4,
    sill_h=0.45,
    head_h=2.7,
    floor_finish=0.012,
    cutaway_h=2.4,         # wall height kept in the isometric cutaway
)

# ---------------------------------------------------------------- dimension pairs used to fit the scale
# (room, axis, span in px between the traced room-side faces, schedule metres)
SCALE_PAIRS = [
    ("KITCHEN", "x", 1117 - 952, 3.54), ("KITCHEN", "y", 158 - 32, 2.75),
    ("UTILITY", "x", 952 - 797, 3.52), ("UTILITY", "y", 107 - 32, 1.60),
    ("STAFF_BATH", "x", 952 - 890, 1.25), ("STAFF_BATH", "y", 158 - 107, 1.07),
    ("BEDROOM_1", "x", 877 - 707, 3.65), ("BEDROOM_1", "y", 397 - 175, 4.85),
    ("BATHROOM_1", "x", 950 - 877, 1.52), ("BATHROOM_1", "y", 337 - 210, 2.75),
    ("MASTER_BEDROOM", "x", 921 - 707, 4.66), ("MASTER_BEDROOM", "y", 617 - 397, 4.77),
    ("MASTER_BATH", "x", 1007 - 921, 1.95),
    ("BEDROOM_2", "x", 1348 - 1192, 3.33),
    ("BATHROOM_2", "x", 1262 - 1192, 1.52), ("BATHROOM_2", "y", 305 - 175, 2.85),
    ("LIVING", "x", 1192 - 1011, 3.86), ("LIVING", "y", 497 - 317, 3.80),
    ("DINING", "x", 1192 - 1018, 3.71),
]


def fit_scale():
    """Least-squares px-per-metre through the origin, plus per-pair residuals in metres."""
    s = sum(p * m for _, _, p, m in SCALE_PAIRS) / sum(m * m for _, _, _, m in SCALE_PAIRS)
    res = [dict(room=r, axis=a, px=p, schedule_m=m, traced_m=round(p / s, 3), diff_m=round(p / s - m, 3))
           for r, a, p, m in SCALE_PAIRS]
    return s, res


PX_PER_M, SCALE_RESIDUALS = fit_scale()


def m(px, py):
    """Image pixel -> Blender metres (plan-up = +Y)."""
    return ((px - ORIGIN_PX[0]) / PX_PER_M, -(py - ORIGIN_PX[1]) / PX_PER_M)


def mx(px):
    return (px - ORIGIN_PX[0]) / PX_PER_M


def my(py):
    return -(py - ORIGIN_PX[1]) / PX_PER_M


# ---------------------------------------------------------------- north
# needle on the drawing runs from (1504.5, 693.8) to (1518, 650) px: 17.2 deg clockwise of plan-up
NORTH_DEG_CW_FROM_UP = math.degrees(math.atan2(1518 - 1504.5, 693.8 - 650))

# ---------------------------------------------------------------- walls
# axis "h": runs along x at y = line; "v": runs along y at x = line
# side for ext walls: which way the thickness grows from the traced face (+1 = towards +px / +py)
WALLS = [
    # --- structural core around kitchen / utility (drawn solid)
    dict(name="CORE_Kitchen_North", kind="core", rect=(787, 16, 1130, 32)),
    dict(name="CORE_Kitchen_West", kind="core", rect=(787, 16, 797, 175)),
    dict(name="CORE_Kitchen_East", kind="core", rect=(1117, 16, 1130, 175)),
    dict(name="CORE_Kitchen_South", kind="core", rect=(787, 158, 1130, 175),
         openings=[(1040, 1082, "door", "D_Kitchen")]),
    dict(name="CORE_MasterBath_East", kind="core", rect=(1007, 485, 1030, 624)),
    # --- exterior envelope (traced room-side face)
    dict(name="EXT_West", kind="ext", axis="v", line=707, span=(175, 617), side=-1, corners=(1, 1),
         openings=[(182, 292, "window", "W_Bedroom1_West"), (512, 610, "window", "W_Master_West")]),
    dict(name="EXT_North_Bedroom1", kind="ext", axis="h", line=175, span=(707, 787), side=-1, corners=(1, 0),
         openings=[(713, 781, "window", "W_Bedroom1_North")]),
    dict(name="EXT_South_Master", kind="ext", axis="h", line=617, span=(707, 1007), side=+1, corners=(1, 0),
         openings=[(714, 914, "window", "W_Master_South")]),
    dict(name="EXT_South_Living", kind="ext", axis="h", line=497, span=(1030, 1316), side=+1,
         openings=[(1036, 1186, "window", "W_Living_South"), (1200, 1310, "window", "W_Bedroom2_South")]),
    dict(name="EXT_East_Bedroom2", kind="ext", axis="v", line=1348, span=(305, 486), side=+1, corners=(1, 0)),
    dict(name="EXT_North_Bedroom2_Shaft", kind="ext", axis="h", line=305, span=(1262, 1348), side=-1, corners=(0, 1)),
    dict(name="EXT_West_Shaft", kind="ext", axis="v", line=1262, span=(175, 305), side=+1, corners=(1, 0)),
    dict(name="EXT_Entry_Foyer", kind="ext", axis="h", line=175, span=(1130, 1262), side=-1, corners=(0, 1),
         openings=[(1135, 1185, "entry", "D_Entry")]),
    # --- interior partitions (centre line)
    dict(name="INT_Bedroom1_Bath1", kind="int", axis="v", line=877, span=(175, 337)),
    dict(name="INT_Bath1_Duct", kind="int", axis="h", line=210, span=(877, 950)),
    dict(name="INT_Bath1_South", kind="int", axis="h", line=337, span=(877, 950),
         openings=[(885, 922, "door", "D_Bath1")]),
    dict(name="INT_Bath1_Passage", kind="int", axis="v", line=950, span=(175, 397),
         openings=[(348, 391, "door", "D_Bedroom1")]),
    dict(name="INT_Bedroom1_Master", kind="int", axis="h", line=397, span=(707, 1011),
         openings=[(959, 1002, "door", "D_Master")]),
    dict(name="INT_Powder_South", kind="int", axis="h", line=290, span=(950, 1018),
         openings=[(955, 990, "door", "D_Powder")]),
    dict(name="INT_Powder_East", kind="int", axis="v", line=1018, span=(175, 290)),
    dict(name="INT_TV_Feature", kind="int", axis="v", line=1011, span=(345, 485)),
    dict(name="INT_Master_Bath", kind="int", axis="v", line=921, span=(455, 617)),
    dict(name="INT_MasterBath_North", kind="int", axis="h", line=455, span=(921, 1011),
         openings=[(927, 963, "door", "D_MasterBath")]),
    dict(name="INT_Bath2_West", kind="int", axis="v", line=1192, span=(175, 305),
         openings=[(262, 300, "door", "D_Bath2")]),
    dict(name="INT_Bath2_South", kind="int", axis="h", line=305, span=(1192, 1262)),
    dict(name="INT_Bedroom2_West", kind="int", axis="v", line=1192, span=(305, 497),
         openings=[(310, 352, "door", "D_Bedroom2")]),
    dict(name="INT_Utility_Kitchen", kind="int", axis="v", line=952, span=(32, 158),
         openings=[(58, 100, "door", "D_Utility"), (110, 143, "door", "D_StaffBath")]),
    dict(name="INT_Utility_South", kind="int", axis="h", line=107, span=(797, 952)),
    dict(name="INT_StaffBath_West", kind="int", axis="v", line=890, span=(107, 158)),
]

COLUMNS = [dict(name="COL_SouthEast", rect=(1316, 486, 1381, 551))]

# lift core shown for context only (not part of the apartment, not validated)
CONTEXT = [
    dict(name="CTX_Lift_North", rect=(1222, 24, 1475, 35)),
    dict(name="CTX_Lift_West", rect=(1222, 24, 1232, 175)),
    dict(name="CTX_Lift_East", rect=(1465, 24, 1475, 175)),
    dict(name="CTX_Lift_Mid", rect=(1345, 35, 1352, 158)),
    dict(name="CTX_Lift_South", rect=(1222, 158, 1475, 175)),
]

# ---------------------------------------------------------------- doors: hinge end, swing direction
# hinge: "a" = low end of the opening along the wall, "b" = high end
# into: room the leaf swings into (+1 = towards +px / +py side of the wall)
DOORS = {
    "D_Entry": dict(hinge="b", into=+1, room="DINING", leaf_t=0.055, open_deg=90),
    "D_Kitchen": dict(hinge="b", into=-1, room="KITCHEN"),
    "D_Utility": dict(hinge="b", into=-1, room="UTILITY"),
    "D_StaffBath": dict(hinge="a", into=-1, room="STAFF_BATH"),
    "D_Bath1": dict(hinge="a", into=-1, room="BATHROOM_1"),
    "D_Bedroom1": dict(hinge="b", into=-1, room="BEDROOM_1"),
    "D_Master": dict(hinge="b", into=+1, room="MASTER_BEDROOM"),
    "D_Powder": dict(hinge="a", into=-1, room="POWDER"),
    "D_MasterBath": dict(hinge="a", into=+1, room="MASTER_BATH"),
    "D_Bath2": dict(hinge="b", into=+1, room="BATHROOM_2"),
    "D_Bedroom2": dict(hinge="a", into=+1, room="BEDROOM_2"),
}

# ---------------------------------------------------------------- rooms (room-side polygons, px)
ROOMS = {
    "DINING": dict(coll="ROOM_Dining", floor="MAT_Travertine", label="1 Dining / Entry",
                   poly=[(1018, 175), (1192, 175), (1192, 317), (1011, 317), (1011, 290), (1018, 290)]),
    "LIVING": dict(coll="ROOM_Living", floor="MAT_Travertine", label="2 Living",
                   poly=[(1011, 317), (1192, 317), (1192, 497), (1030, 497), (1030, 485), (1011, 485)]),
    "KITCHEN": dict(coll="ROOM_Kitchen", floor="MAT_Greige_Stone", label="3 Kitchen",
                    poly=[(952, 32), (1117, 32), (1117, 158), (952, 158)]),
    "UTILITY": dict(coll="ROOM_Utility", floor="MAT_Greige_Stone", label="4 Utility",
                    poly=[(797, 32), (952, 32), (952, 107), (797, 107)]),
    "STAFF_BATH": dict(coll="ROOM_Utility", floor="MAT_Greige_Stone", label="5 Staff bathroom",
                       poly=[(890, 107), (952, 107), (952, 158), (890, 158)]),
    "POWDER": dict(coll="ROOM_Bathrooms", floor="MAT_Greige_Stone", label="6 Powder room",
                   poly=[(950, 175), (1018, 175), (1018, 290), (950, 290)]),
    "PASSAGE": dict(coll="ROOM_Dining", floor="MAT_Travertine", label="7 Passage",
                    poly=[(950, 290), (1011, 290), (1011, 397), (950, 397)]),
    "BEDROOM_1": dict(coll="ROOM_Bedroom_01", floor="MAT_Warm_Oak", label="8 Bedroom 1",
                      poly=[(707, 175), (877, 175), (877, 337), (950, 337), (950, 397), (707, 397)]),
    "BATHROOM_1": dict(coll="ROOM_Bathrooms", floor="MAT_Greige_Stone", label="9 Bathroom 1",
                       poly=[(877, 210), (950, 210), (950, 337), (877, 337)]),
    "MASTER_BEDROOM": dict(coll="ROOM_Master", floor="MAT_Warm_Oak", label="10 Master bedroom",
                           poly=[(707, 397), (1011, 397), (1011, 455), (921, 455), (921, 617), (707, 617)]),
    "MASTER_BATH": dict(coll="ROOM_Bathrooms", floor="MAT_Greige_Stone", label="11 Master bathroom",
                        poly=[(921, 455), (1007, 455), (1007, 617), (921, 617)]),
    "BEDROOM_2": dict(coll="ROOM_Bedroom_02", floor="MAT_Warm_Oak", label="12 Bedroom 2",
                      poly=[(1192, 305), (1348, 305), (1348, 486), (1316, 486), (1316, 497), (1192, 497)]),
    "BATHROOM_2": dict(coll="ROOM_Bathrooms", floor="MAT_Greige_Stone", label="13 Bathroom 2",
                       poly=[(1192, 175), (1262, 175), (1262, 305), (1192, 305)]),
}

FOYER = [(1130, 16), (1222, 16), (1222, 175), (1130, 175)]          # restricted common area, context only
DUCTS = [dict(name="DUCT_Utility", rect=(797, 107, 890, 158)), dict(name="DUCT_Bath1", rect=(877, 175, 950, 210)),
         dict(name="DUCT_East", rect=(1262, 175, 1430, 305))]

# schedule from the drawing: (feet text, metres, sq ft) of the main rectangle
SCHEDULE = {
    "DINING": ((3.71, 3.00), 119.80), "LIVING": ((3.86, 3.80), 157.88), "KITCHEN": ((3.54, 2.75), 104.78),
    "UTILITY": ((3.52, 1.60), 60.62), "STAFF_BATH": ((1.25, 1.07), 14.39), "POWDER": ((1.50, 2.20), 35.52),
    "PASSAGE": ((1.35, 1.85), 26.88), "BEDROOM_1": ((3.65, 4.85), 190.54), "BATHROOM_1": ((1.52, 2.75), 44.99),
    "MASTER_BEDROOM": ((4.66, 4.77), 239.26), "MASTER_BATH": ((1.95, 2.00), 41.97),
    "BEDROOM_2": ((3.33, 3.87), 138.71), "BATHROOM_2": ((1.52, 2.85), 46.62),
}

# expected adjacency through doors / open plan, read from the drawing
ADJACENCY = [
    ("FOYER", "DINING", "D_Entry"), ("DINING", "LIVING", "open"), ("DINING", "PASSAGE", "open"),
    ("LIVING", "PASSAGE", "open"), ("DINING", "KITCHEN", "D_Kitchen"), ("KITCHEN", "UTILITY", "D_Utility"),
    ("KITCHEN", "STAFF_BATH", "D_StaffBath"), ("PASSAGE", "POWDER", "D_Powder"),
    ("PASSAGE", "BEDROOM_1", "D_Bedroom1"), ("BEDROOM_1", "BATHROOM_1", "D_Bath1"),
    ("PASSAGE", "MASTER_BEDROOM", "D_Master"), ("MASTER_BEDROOM", "MASTER_BATH", "D_MasterBath"),
    ("DINING", "BATHROOM_2", "D_Bath2"), ("LIVING", "BEDROOM_2", "D_Bedroom2"),
]

# where the trace had to interpret the drawing (reported in architectural_validation.json)
UNCERTAINTIES = [
    "Scale is fitted from the room schedule (least squares over 19 dimensioned spans); the drawing carries no "
    "dimension strings or scale bar on the unit plan, and the JPEG is ~46 px/m, so traced faces are good to about "
    "+/-2 px (+/-0.05 m).",
    "Exterior and partition thicknesses are not dimensioned. Exterior = 0.23 m and interior = 0.115 m are applied "
    "as provisional values from the room-side faces; solid-black core walls and the south-east column are kept "
    "at their drawn thickness.",
    "Wall height, sill and head heights and door heights are not on the drawing: 3.0 m ceiling, 0.45 m sill, "
    "2.70 m window head, 2.10 m doors and 2.40 m entry door are assumptions.",
    "Bedroom 1 and master windows carry labels like '2.00M X 0.40M' with a glazing line about 0.45 m outside the "
    "wall; read as a 0.40 m deep external ledge with a glass guard, as in the supplied isometric render.",
    "Bedroom 2 is traced to the wardrobe-side wall line at 4.17 m deep; the schedule gives 3.87 m. The schedule "
    "figure probably excludes the 0.6 m wardrobe zone. Left as drawn.",
    "Powder room door position and swing are read from a partly hidden arc; placed in the passage-side wall.",
    "The lift lobby, lifts, foyer and service ducts are outside the apartment and are modelled for context only.",
    "Door hinge sides follow the arcs on the drawing where legible; the bathroom 2 and powder room hinges are "
    "interpretations.",
    "No ceiling plan is supplied: flat 3.0 m ceilings with recessed downlights are assumed throughout.",
    "Site location (Mumbai, from 'Gokhale Road South' on the key plan), date and time used for the sun are "
    "provisional.",
]
