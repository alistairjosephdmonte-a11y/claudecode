"""Reusable environments. Each builder creates its geometry at the local origin inside the given collection.

PHASE 2 (run headless):
    blender -b --factory-startup --python scripts/environments.py -- [--render-check]
writes scenes/BC001_LOC_BOARDROOM.blend, _STORE, _WAREHOUSE, _ARCHIVE (linked into the master by shot_builder.py).
Geometry only: lighting is shot-specific and lives in the master, so a linked set can be relit per shot.
No historical signage, logos or seating assignments are modelled."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import assets as A  # noqa: E402
import config as C  # noqa: E402

# Fixed geography (metres, local to each set) - shot_builder places cameras against these.
BOARDROOM = dict(x0=-5.0, x1=5.0, y0=-3.5, y1=3.5, h=3.0, table=(5.0, 1.5, 0.75), door=(-5.0, -2.0), window_y=3.5)
STORE = dict(x0=-8.0, x1=8.0, y0=-6.0, y1=10.0, h=3.6, counter=(5.0, -3.0), returns=(-6.6, -5.55), aisles=(-5.0, -2.0, 1.0))
WAREHOUSE = dict(x0=-15.0, x1=15.0, y0=-10.0, y1=10.0, h=7.0, belts=(0.0, 3.0), pack_y=-4.0, sort_y=6.5)
ARCHIVE = dict(table=(3.2, 2.0, 0.9))


# ---------------------------------------------------------------- ENV_02 BOARDROOM (representative, September 2000)
def build_boardroom(c, M):
    B = BOARDROOM
    x0, x1, y0, y1, h = B["x0"], B["x1"], B["y0"], B["y1"], B["h"]
    A.box("BR_Floor_Carpet", c, (0, 0, -0.02), (x1 - x0, y1 - y0, 0.04), M["carpet"])
    A.box("BR_Ceiling", c, (0, 0, h + 0.05), (x1 - x0, y1 - y0, 0.1), M["wall_paint"])
    A.box("BR_Wall_South", c, (0, y0 - 0.05, h / 2), (x1 - x0, 0.1, h), M["wall_paint"])
    A.box("BR_Wall_East", c, (x1 + 0.05, 0, h / 2), (0.1, y1 - y0, h), M["wall_paint"])
    # west wall with the fixed doorway
    dy = B["door"][1]
    A.box("BR_Wall_West_A", c, (x0 - 0.05, (y0 + dy - 0.55) / 2, h / 2), (0.1, dy - 0.55 - y0, h), M["wall_paint"])
    A.box("BR_Wall_West_B", c, (x0 - 0.05, (dy + 0.55 + y1) / 2, h / 2), (0.1, y1 - dy - 0.55, h), M["wall_paint"])
    A.box("BR_Wall_West_Lintel", c, (x0 - 0.05, dy, 2.55), (0.1, 1.1, 0.9), M["wall_paint"])
    A.box("BR_Door_Leaf", c, (x0 - 0.02, dy, 1.05), (0.05, 1.0, 2.1), M["wood"], bevel=0.005)
    A.box("BR_Door_Frame", c, (x0 + 0.01, dy, 1.08), (0.03, 1.12, 2.18), M["metal_dark"])
    A.box("BR_Door_Handle", c, (x0 + 0.05, dy + 0.38, 1.0), (0.04, 0.12, 0.03), M["steel"])
    # fixed window wall (north): glass with mullions, sill and spandrel
    A.box("BR_Window_Sill", c, (0, y1 - 0.1, 0.4), (x1 - x0, 0.25, 0.8), M["wood"])
    A.box("BR_Window_Glass", c, (0, y1 + 0.02, 1.85), (x1 - x0, 0.02, 2.1), M["glass"])
    for i in range(9):
        x = x0 + i * (x1 - x0) / 8
        A.box(f"BR_Window_Mullion_{i}", c, (x, y1, 1.85), (0.06, 0.08, 2.1), M["metal_dark"])
    A.box("BR_Window_Header", c, (0, y1, 2.95), (x1 - x0, 0.12, 0.1), M["metal_dark"])
    # view through the window: neutral dusk-lit city massing (no identifiable buildings or signage)
    rnd = random.Random(7)
    for i in range(26):
        bx, by = rnd.uniform(-60, 60), rnd.uniform(35, 160)
        bh = rnd.uniform(25, 110)
        A.box(f"BR_View_Building_{i:02d}", c, (bx, by, bh / 2 - 12), (rnd.uniform(10, 22), rnd.uniform(10, 22), bh), M["concrete"])
    A.box("BR_View_Ground", c, (0, 90, -12.5), (200, 140, 1), M["asphalt"])
    # ceiling practicals (recessed panels)
    for i, x in enumerate((-3.0, 0.0, 3.0)):
        for j, y in enumerate((-1.2, 1.2)):
            A.box(f"BR_Ceiling_Light_{i}{j}", c, (x, y, h - 0.01), (1.2, 0.6, 0.02), M["fluoro"])
    # table (rectangular, wood) and eight-to-ten chairs (no seating assignments)
    tx, ty, tz = B["table"]
    A.box("BR_Table_Top", c, (0, 0, tz - 0.025), (tx, ty, 0.05), M["wood"], bevel=0.01)
    for s in (-1, 1):
        A.box(f"BR_Table_Pedestal_{s:+d}", c, (s * tx * 0.3, 0, (tz - 0.05) / 2), (0.5, ty * 0.55, tz - 0.05), M["wood"])
    chair_spots = [(x, s * (ty / 2 + 0.45), -s * 90) for s in (-1, 1) for x in (-1.8, -0.6, 0.6, 1.8)]
    chair_spots += [(-tx / 2 - 0.55, 0, 0), (tx / 2 + 0.55, 0, 180)]
    for i, (x, y, yaw) in enumerate(chair_spots):
        root = A.empty(f"BR_Chair_{i:02d}", c, (x, y, 0), 0.3)
        root.rotation_euler.z = math.radians(yaw)
        A.box(f"BR_Chair_{i:02d}_Seat", c, (0, 0, 0.47), (0.5, 0.5, 0.08), M["fabric"], parent=root, bevel=0.02)
        A.box(f"BR_Chair_{i:02d}_Back", c, (-0.24, 0, 0.82), (0.07, 0.48, 0.62), M["fabric"], parent=root, bevel=0.02)
        A.obj(f"BR_Chair_{i:02d}_Column", A.mesh_cyl(f"BR_ChairColumn_{i}", 0.03, 0.42, M["steel"], 12), c, (0, 0, 0.03), parent=root)
        for k in range(5):
            a = 2 * math.pi * k / 5
            A.box(f"BR_Chair_{i:02d}_Leg_{k}", c, (0.17 * math.cos(a), 0.17 * math.sin(a), 0.04), (0.34, 0.04, 0.03),
                  M["metal_dark"], rot=(0, 0, a), parent=root)
    A.box("BR_Credenza", c, (x1 - 0.3, 0, 0.42), (0.5, 3.0, 0.84), M["wood"], bevel=0.01)
    A.box("BR_Phone_Conference", c, (0.0, 0.0, tz + 0.02), (0.22, 0.22, 0.04), M["plastic_black"], bevel=0.01)
    for i, (x, y) in enumerate(((-1.8, -0.55), (0.6, 0.55), (1.8, -0.55))):
        A.box(f"BR_Notepad_{i}", c, (x, y, tz + 0.004), (0.21, 0.28, 0.008), M["paper_white"])
    return c


# ---------------------------------------------------------------- ENV_03 STORE (representative late-1990s/early-2000s video store)
def _shelf_cases(name, c, M, origin, length, levels, depth_side, density, seed, along="Y"):
    """One mesh of media cases on a shelf run: random case widths/colours, no titles or artwork."""
    rnd = random.Random(seed)
    boxes = []
    for lv, z in enumerate(levels):
        t = 0.0
        while t < length - 0.05:
            w = rnd.choice((0.02, 0.02, 0.03))                     # DVD / VHS spine thickness
            if rnd.random() < density:
                pos = (origin[0] + (t if along == "X" else 0), origin[1] + (t if along == "Y" else 0), z + 0.095)
                size = (w, 0.135, 0.19) if along == "X" else (0.135, w, 0.19)
                if along == "Y":
                    pos = (pos[0] + depth_side * 0.07, pos[1], pos[2])
                else:
                    pos = (pos[0], pos[1] + depth_side * 0.07, pos[2])
                boxes.append((pos, size, rnd.choice(M["case_colors"])))
            t += w + 0.004
    return A.obj(name, A.mesh_boxes(name, boxes), c) if boxes else None


def build_store(c_base, c_full, c_reduced, M):
    S = STORE
    x0, x1, y0, y1, h = S["x0"], S["x1"], S["y0"], S["y1"], S["h"]
    c = c_base
    A.box("ST_Floor_Carpet", c, ((x0 + x1) / 2, (y0 + y1) / 2, -0.02), (x1 - x0, y1 - y0, 0.04), M["carpet"])
    A.box("ST_Ceiling", c, ((x0 + x1) / 2, (y0 + y1) / 2, h + 0.05), (x1 - x0, y1 - y0, 0.1), M["wall_paint"])
    A.box("ST_Wall_Back", c, ((x0 + x1) / 2, y1 + 0.05, h / 2), (x1 - x0, 0.1, h), M["wall_paint"])
    A.box("ST_Wall_West", c, (x0 - 0.05, (y0 + y1) / 2, h / 2), (0.1, y1 - y0, h), M["wall_paint"])
    A.box("ST_Wall_East", c, (x1 + 0.05, (y0 + y1) / 2, h / 2), (0.1, y1 - y0, h), M["wall_paint"])
    # fixed entrance: glass storefront with double doors at x = 0
    A.box("ST_Front_Glass_W", c, ((x0 - 1.2) / 2, y0, 1.4), (x0 * -1 - 1.2, 0.03, 2.8), M["glass"])
    A.box("ST_Front_Glass_E", c, ((x1 + 1.2) / 2, y0, 1.4), (x1 - 1.2, 0.03, 2.8), M["glass"])
    for s in (-1, 1):
        A.box(f"ST_Door_{s:+d}", c, (s * 0.6, y0, 1.15), (1.15, 0.04, 2.3), M["glass_tint"])
        A.box(f"ST_Door_Handle_{s:+d}", c, (s * 0.12, y0 - 0.04, 1.1), (0.03, 0.03, 0.6), M["steel"])
    for i in range(9):
        A.box(f"ST_Front_Mullion_{i}", c, (x0 + i * (x1 - x0) / 8, y0, 1.4), (0.08, 0.08, 2.8), M["metal_dark"])
    A.box("ST_Front_Transom", c, ((x0 + x1) / 2, y0, 3.2), (x1 - x0, 0.2, 0.8), M["wall_paint"])
    # exterior fascia: blank editorial-colour panel (no lettering; signage pending approved brand reference)
    A.box("ST_Fascia_Panel_Blank", c, (0, y0 - 0.18, 4.3), (11.0, 0.25, 1.4), M["blue"], bevel=0.02)
    A.box("ST_Fascia_Accent_Blank", c, (0, y0 - 0.32, 4.3), (3.2, 0.06, 0.9), M["yellow"], bevel=0.02)
    A.box("ST_Exterior_Parapet", c, ((x0 + x1) / 2, y0 - 0.02, 4.4), (x1 - x0 + 0.4, 0.3, 1.8), M["concrete"])
    A.box("ST_Sidewalk", c, ((x0 + x1) / 2, y0 - 2.5, -0.05), (x1 - x0 + 10, 5.0, 0.1), M["concrete"])
    A.box("ST_Parking_Lot", c, ((x0 + x1) / 2, y0 - 20, -0.08), (60, 30, 0.04), M["asphalt"])
    for i in range(12):
        A.box(f"ST_Parking_Stripe_{i}", c, (-16 + i * 3.0, y0 - 11, -0.055), (0.12, 5.0, 0.01), M["paper_white"])
    # returns area (drop slot by the door) and checkout counter with era-appropriate registers
    rx, ry = S["returns"]
    A.box("ST_Returns_Box", c, (rx, ry + 0.4, 0.55), (0.8, 0.6, 1.1), M["metal_paint"], bevel=0.02)
    A.box("ST_Returns_Slot", c, (rx, ry + 0.09, 0.95), (0.45, 0.02, 0.06), M["plastic_black"])
    cx, cy = S["counter"]
    A.box("ST_Counter_Front", c, (cx, cy, 0.52), (4.0, 0.7, 1.04), M["wood_light"], bevel=0.02)
    A.box("ST_Counter_Top", c, (cx, cy, 1.06), (4.1, 0.8, 0.04), M["plastic_beige"], bevel=0.005)
    for i, x in enumerate((cx - 1.2, cx + 0.6)):
        A.box(f"ST_Register_{i}", c, (x, cy + 0.15, 1.15), (0.42, 0.38, 0.14), M["plastic_beige"], bevel=0.01)
        A.box(f"ST_Register_{i}_Monitor", c, (x, cy + 0.25, 1.38), (0.36, 0.3, 0.3), M["plastic_beige"], bevel=0.02)
        A.box(f"ST_Register_{i}_Screen", c, (x, cy + 0.095, 1.39), (0.27, 0.01, 0.2), M["crt"])
        A.box(f"ST_Register_{i}_CardReader", c, (x + 0.3, cy - 0.1, 1.11), (0.1, 0.16, 0.05), M["plastic_black"])
    for i, x in enumerate((-4.0, 0.0, 4.0)):                         # ceiling-hung CRT trailer monitors
        A.box(f"ST_Trailer_TV_{i}", c, (x, y1 - 0.5, 2.7), (0.75, 0.55, 0.55), M["plastic_black"], bevel=0.02)
        A.box(f"ST_Trailer_TV_{i}_Screen", c, (x, y1 - 0.78, 2.7), (0.6, 0.01, 0.42), M["crt"])
    for i in range(4):
        for j in range(4):
            A.box(f"ST_Fluorescent_{i}{j}", c, (-6 + 4 * i, -3 + 3.6 * j, h - 0.02), (1.2, 0.3, 0.03), M["fluoro"])
    # modular gondola shelving (fixed), inventory meshes live in the FULL / REDUCED collections
    levels = (0.15, 0.6, 1.05, 1.5)
    for i, x in enumerate(S["aisles"]):
        A.box(f"ST_Gondola_{i}_Spine", c, (x, 3.5, 0.95), (0.06, 8.0, 1.9), M["metal_paint"])
        A.box(f"ST_Gondola_{i}_Base", c, (x, 3.5, 0.06), (0.75, 8.0, 0.12), M["metal_paint"])
        for z in levels:
            A.box(f"ST_Gondola_{i}_Shelf_{z}", c, (x, 3.5, z), (0.72, 8.0, 0.02), M["metal_paint"])
        A.box(f"ST_Gondola_{i}_Header_Blank", c, (x, -0.6, 2.05), (0.7, 0.04, 0.35), M["blue"])
        for side in (-1, 1):
            _shelf_cases(f"ST_Inventory_Full_G{i}_{side:+d}", c_full, M, (x, -0.45), 7.9, levels, side, 0.95, 100 + i * 7 + side)
            _shelf_cases(f"ST_Inventory_Reduced_G{i}_{side:+d}", c_reduced, M, (x, -0.45), 7.9, levels, side, 0.28, 300 + i * 7 + side)
    for wall, (x, along_y) in (("W", (x0 + 0.25, True)), ("E", (x1 - 0.25, True))):
        A.box(f"ST_WallShelf_{wall}_Back", c, (x, 4.5, 1.1), (0.4, 9.0, 2.2), M["metal_paint"])
        _shelf_cases(f"ST_Inventory_Full_Wall_{wall}", c_full, M, (x, 0.1), 8.8, (0.2, 0.7, 1.2, 1.7), 1 if wall == "W" else -1, 0.95, 21 if wall == "W" else 22)
        _shelf_cases(f"ST_Inventory_Reduced_Wall_{wall}", c_reduced, M, (x, 0.1), 8.8, (0.2, 0.7, 1.2, 1.7), 1 if wall == "W" else -1, 0.2, 23 if wall == "W" else 24)
    A.box("ST_NewRelease_Wall", c, (0, y1 - 0.25, 1.1), (12.0, 0.4, 2.2), M["metal_paint"])
    _shelf_cases("ST_Inventory_Full_NewRelease", c_full, M, (-5.9, y1 - 0.25), 11.8, (0.2, 0.7, 1.2, 1.7), -1, 1.0, 31, along="X")
    _shelf_cases("ST_Inventory_Reduced_NewRelease", c_reduced, M, (-5.9, y1 - 0.25), 11.8, (0.2, 0.7, 1.2, 1.7), -1, 0.15, 32, along="X")
    return c


# ---------------------------------------------------------------- ENV_04 DVD FULFILLMENT (representative, not a specific facility)
def build_warehouse(c, M):
    W = WAREHOUSE
    A.box("WH_Floor", c, (0, 0, -0.05), (W["x1"] - W["x0"], W["y1"] - W["y0"], 0.1), M["concrete"])
    A.box("WH_Wall_North", c, (0, W["y1"] + 0.1, W["h"] / 2), (W["x1"] - W["x0"], 0.2, W["h"]), M["metal_paint"])
    A.box("WH_Wall_West", c, (W["x0"] - 0.1, 0, W["h"] / 2), (0.2, W["y1"] - W["y0"], W["h"]), M["metal_paint"])
    A.box("WH_Wall_East", c, (W["x1"] + 0.1, 0, W["h"] / 2), (0.2, W["y1"] - W["y0"], W["h"]), M["metal_paint"])
    A.box("WH_Roof", c, (0, 0, W["h"] + 0.1), (W["x1"] - W["x0"], W["y1"] - W["y0"], 0.2), M["metal_dark"])
    for i in range(6):
        A.box(f"WH_Roof_Truss_{i}", c, (-12.5 + 5 * i, 0, W["h"] - 0.3), (0.25, W["y1"] - W["y0"], 0.4), M["metal_dark"])
        A.box(f"WH_Pendant_{i}", c, (-12.5 + 5 * i, 1.5, W["h"] - 1.4), (0.6, 0.6, 0.12), M["fluoro"])
    for k, y in enumerate(W["belts"]):                                  # conveyor sections: belt, side rails, legs, rollers
        A.box(f"WH_Conveyor_{k}_Belt", c, (0, y, 0.85), (24.0, 0.6, 0.04), M["plastic_black"])
        for s in (-1, 1):
            A.box(f"WH_Conveyor_{k}_Rail_{s:+d}", c, (0, y + s * 0.33, 0.9), (24.0, 0.04, 0.12), M["steel"])
        for i in range(13):
            for s in (-1, 1):
                A.box(f"WH_Conveyor_{k}_Leg_{i}_{s:+d}", c, (-12 + 2 * i, y + s * 0.28, 0.42), (0.05, 0.05, 0.84), M["metal_dark"])
    for i in range(10):                                                 # sorting bins
        for j in range(5):
            A.box(f"WH_SortBin_{i}_{j}", c, (-9 + 2.0 * i, W["sort_y"], 0.35 + 0.42 * j), (1.8, 0.6, 0.36), M["plastic_beige"], bevel=0.01)
    A.box("WH_SortRack_Frame", c, (0, W["sort_y"] + 0.35, 1.25), (20.4, 0.08, 2.5), M["metal_dark"])
    for i in range(4):                                                  # packing tables with mail trays
        x = -9 + 6 * i
        A.box(f"WH_PackTable_{i}_Top", c, (x, W["pack_y"], 0.9), (2.4, 1.0, 0.05), M["wood_light"], bevel=0.005)
        for sx in (-1, 1):
            for sy in (-1, 1):
                A.box(f"WH_PackTable_{i}_Leg_{sx:+d}{sy:+d}", c, (x + sx * 1.1, W["pack_y"] + sy * 0.42, 0.44), (0.05, 0.05, 0.88), M["metal_dark"])
        A.box(f"WH_MailTray_{i}", c, (x + 0.7, W["pack_y"] + 0.15, 1.0), (0.6, 0.35, 0.15), M["plastic_beige"], bevel=0.01)
    for i in range(5):                                                  # shipping carts / containers
        A.box(f"WH_ShippingCart_{i}", c, (11.5, -7.5 + 1.6 * i, 0.75), (1.2, 1.2, 1.4), M["cardboard"], bevel=0.02)
    return c


# ---------------------------------------------------------------- ENV_05 ARCHIVE LIGHT TABLE
def build_archive(c, M):
    tx, ty, tz = ARCHIVE["table"]
    A.box("AR_Floor", c, (0, 0, -0.02), (14, 14, 0.04), M["black"])
    A.box("AR_Table_Top", c, (0, 0, tz - 0.03), (tx, ty, 0.06), M["metal_dark"], bevel=0.01)
    A.box("AR_Table_Felt", c, (0, 0, tz + 0.001), (tx - 0.1, ty - 0.1, 0.002), M["black"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            A.box(f"AR_Table_Leg_{sx:+d}{sy:+d}", c, (sx * (tx / 2 - 0.1), sy * (ty / 2 - 0.1), (tz - 0.06) / 2), (0.08, 0.08, tz - 0.06), M["metal_dark"])
    A.obj("AR_Lamp_Shade", A.mesh_cyl("AR_Lamp_Shade", 0.42, 0.3, M["metal_dark"], 32, 0.12), c, (0, 0, 2.3))
    A.box("AR_Lamp_Cord", c, (0, 0, 3.0), (0.01, 0.01, 1.4), M["plastic_black"])
    A.box("AR_Ruler", c, (-tx / 2 + 0.25, -ty / 2 + 0.12, tz + 0.004), (0.4, 0.035, 0.004), M["steel"])
    A.box("AR_Pencil", c, (tx / 2 - 0.3, -ty / 2 + 0.15, tz + 0.006), (0.18, 0.008, 0.008), M["yellow"], rot=(0, 0, 0.4))
    A.obj("AR_Loupe", A.mesh_cyl("AR_Loupe", 0.03, 0.045, M["plastic_black"], 20), c, (tx / 2 - 0.25, ty / 2 - 0.2, tz))
    for i in range(3):
        A.box(f"AR_FolderStack_{i}", c, (-tx / 2 + 0.35, ty / 2 - 0.3, tz + 0.01 + 0.012 * i), (0.32, 0.24, 0.01), M["cardboard"], rot=(0, 0, 0.05 * i))
    return c


# ---------------------------------------------------------------- master-only sets
def build_dallas(c, M):
    """Stylised downtown massing at dusk. No identifiable buildings, company signage or landmarks are asserted;
    a generic observation-tower proxy is tagged REF_PENDING until verified reference geometry is supplied."""
    A.box("DAL_Ground", c, (0, 0, -0.1), (1400, 1400, 0.2), M["asphalt"])
    for i in range(-6, 7):
        A.box(f"DAL_Street_NS_{i}", c, (i * 80 + 40, 0, -0.005), (12, 1400, 0.01), M["concrete"])
        A.box(f"DAL_Street_EW_{i}", c, (0, i * 80 + 40, -0.004), (1400, 12, 0.01), M["concrete"])
    rnd = random.Random(2000)
    win = A.mat_noise("MAT_Tower_Windows_Dusk", (0.05, 0.06, 0.08), (0.55, 0.45, 0.3), 3.5, 0.3, metal=0.2, bump=0.0, kind="wave", direction="Z")
    glass = A.mat_basic("MAT_Tower_Glass_Dusk", (0.12, 0.16, 0.22), 0.12, 0.4)
    k = 0
    for gx in range(-5, 6):
        for gy in range(-5, 6):
            if (gx, gy) == (0, 0):
                continue
            dist = math.hypot(gx, gy)
            for n in range(rnd.randint(1, 3)):
                h = max(20, rnd.gauss(160 - dist * 22, 35))
                w = rnd.uniform(18, 34)
                x = gx * 80 + rnd.uniform(-18, 18)
                y = gy * 80 + rnd.uniform(-18, 18)
                A.box(f"DAL_Tower_{k:03d}", c, (x, y, h / 2), (w, w * rnd.uniform(0.7, 1.3), h), win if rnd.random() < 0.6 else glass)
                k += 1
    tw = A.empty("DAL_ObservationTower_Proxy_REF_PENDING", c, (-260, 170, 0), 5)
    A.obj("DAL_ObsTower_Shaft", A.mesh_cyl("DAL_ObsTower_Shaft", 4.0, 150, M["concrete"], 16), c, (0, 0, 0), parent=tw)
    A.obj("DAL_ObsTower_Sphere", A.mesh_sphere("DAL_ObsTower_Sphere", 16, M["metal_paint"], 24, 12), c, (0, 0, 160), parent=tw)
    # plaza tower for S02 (generic corporate building; no signage)
    A.box("DAL_Plaza_Tower", c, (0, 0, 90), (40, 40, 180), glass)
    A.box("DAL_Plaza_Lobby_Glass", c, (0, -20.2, 4.5), (36, 0.1, 9), M["glass_tint"])
    for i in range(10):
        A.box(f"DAL_Plaza_Lobby_Mullion_{i}", c, (-18 + 4 * i, -20.3, 4.5), (0.2, 0.25, 9), M["metal_dark"])
    A.box("DAL_Plaza_Canopy", c, (0, -23, 9.2), (14, 6, 0.4), M["metal_dark"])
    for s in (-1, 1):
        A.box(f"DAL_Plaza_Door_{s:+d}", c, (s * 1.1, -20.35, 1.4), (2.0, 0.08, 2.8), M["glass"])
    A.box("DAL_Plaza_Paving", c, (0, -34, 0.0), (60, 28, 0.06), M["concrete"])
    for i, x in enumerate((-18, -9, 9, 18)):
        A.box(f"DAL_Plaza_Planter_{i}", c, (x, -32, 0.4), (3.0, 3.0, 0.8), M["concrete"], bevel=0.05)
        A.obj(f"DAL_Plaza_Tree_{i}", A.mesh_sphere(f"DAL_Plaza_Tree_{i}", 1.8, A.mat_basic("MAT_Tree_Foliage", (0.05, 0.09, 0.04), 0.9), 12, 8), c, (x, -32, 3.2))
    return c


def build_desk_vignette(c, M):
    """Representative early-2000s desk: beige CRT and PC. Screen content is an abstract layout (no real website)."""
    A.box("DSK_Floor", c, (0, 0, -0.02), (5, 5, 0.04), M["carpet"])
    A.box("DSK_Wall", c, (0, 1.2, 1.4), (5, 0.1, 2.8), M["wall_paint"])
    A.box("DSK_Desk_Top", c, (0, 0.6, 0.73), (1.5, 0.75, 0.04), M["wood_light"], bevel=0.005)
    for sx in (-1, 1):
        A.box(f"DSK_Desk_Side_{sx:+d}", c, (sx * 0.72, 0.6, 0.36), (0.04, 0.72, 0.72), M["wood_light"])
    A.box("DSK_CRT_Body", c, (0, 0.75, 1.0), (0.42, 0.42, 0.38), M["plastic_beige"], bevel=0.03)
    A.box("DSK_CRT_Bezel", c, (0, 0.535, 1.0), (0.4, 0.02, 0.36), M["plastic_beige"], bevel=0.01)
    A.box("DSK_CRT_Screen", c, (0, 0.522, 1.0), (0.33, 0.005, 0.25), M["crt"])
    # abstract page layout on the screen: header bar, sidebar, content blocks (illustrative, no text)
    for i, (x, z, w, h, m) in enumerate(((0, 1.11, 0.32, 0.03, M["blue"]), (-0.13, 0.98, 0.06, 0.2, M["grey"]),
                                         (0.04, 1.04, 0.22, 0.06, M["paper_white"]), (0.04, 0.95, 0.22, 0.08, M["paper_white"]))):
        A.box(f"DSK_Screen_Layout_{i}", c, (x, 0.518, z), (w, 0.002, h), m)
    A.box("DSK_PC_Tower", c, (0.55, 0.62, 0.95), (0.2, 0.45, 0.4), M["plastic_beige"], bevel=0.01)
    A.box("DSK_Keyboard", c, (0, 0.38, 0.765), (0.46, 0.17, 0.025), M["plastic_beige"], bevel=0.005)
    A.box("DSK_Mouse", c, (0.32, 0.38, 0.765), (0.06, 0.1, 0.03), M["plastic_beige"], bevel=0.01)
    A.box("DSK_Chair_Seat", c, (0, -0.15, 0.47), (0.5, 0.5, 0.08), M["fabric"], bevel=0.02)
    A.box("DSK_Chair_Back", c, (0, -0.42, 0.85), (0.48, 0.07, 0.6), M["fabric"], bevel=0.02)
    A.obj("DSK_Chair_Column", A.mesh_cyl("DSK_Chair_Column", 0.03, 0.42, M["steel"], 12), c, (0, -0.15, 0.03))
    A.box("DSK_Window", c, (-1.6, 1.14, 1.6), (1.0, 0.02, 1.2), A.mat_basic("MAT_Window_Night", (0.02, 0.03, 0.06), 0.2))
    return c


# ---------------------------------------------------------------- PHASE 2 driver
def build_location(kind, out_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = A.library()
    if kind == "BOARDROOM":
        build_boardroom(A.coll("ENV_02_BOARDROOM"), M)
    elif kind == "STORE":
        root = A.coll("ENV_03_BLOCKBUSTER_STORE")
        build_store(A.coll("ENV_03_STORE_BASE", root), A.coll("ENV_03_STORE_INV_FULL", root), A.coll("ENV_03_STORE_INV_REDUCED", root), M)
    elif kind == "WAREHOUSE":
        build_warehouse(A.coll("ENV_04_DVD_FULFILLMENT"), M)
    elif kind == "ARCHIVE":
        build_archive(A.coll("ENV_05_ARCHIVE_LIGHT_TABLE"), M)
    for c in bpy.data.collections:
        c.asset_mark() if hasattr(c, "asset_mark") else None
    bpy.ops.wm.save_as_mainfile(filepath=out_path, relative_remap=True)
    return len(bpy.data.objects)


def render_check(path, out_png):
    """Validation render of a location file with a neutral studio camera + lights."""
    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    c = A.coll("VALIDATION_ONLY")
    cam_d = bpy.data.cameras.new("CAM_VALIDATION")
    cam_d.lens = 35
    cam = A.obj("CAM_VALIDATION", cam_d, c, (-4.4, -3.1, 1.65))
    tgt = Vector((1.5, 1.2, 0.9))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    for i, (x, y) in enumerate(((-3, -1.2), (0, 1.2), (3, -1.2))):
        ld = bpy.data.lights.new(f"LGT_VAL_{i}", "AREA")
        ld.energy, ld.size = 180, 1.2
        A.obj(f"LGT_VAL_{i}", ld, c, (x, y, 2.9))
    sun = bpy.data.lights.new("LGT_VAL_WINDOW", "AREA")
    sun.energy, sun.size, sun.color = 900, 6.0, (0.95, 0.97, 1.0)
    w = A.obj("LGT_VAL_WINDOW", sun, c, (0, 5.5, 1.9))
    w.rotation_euler = (math.radians(-90), 0, 0)
    sc.world = bpy.data.worlds.new("WORLD_VAL")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.4, 0.48, 1)
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 16
    sc.render.resolution_x, sc.render.resolution_y = C.RES_PREVIEW
    sc.view_settings.view_transform = "AgX"
    sc.render.filepath = out_png
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    os.makedirs(C.P["scenes"], exist_ok=True)
    counts = {}
    for kind in ("BOARDROOM", "STORE", "WAREHOUSE", "ARCHIVE"):
        path = os.path.join(C.P["scenes"], C.SCENES[kind])
        counts[kind] = build_location(kind, path)
        print(f"PHASE 2 saved {path} ({counts[kind]} objects)")
    if "--render-check" in sys.argv:
        out = os.path.join(C.P["previews"], "VALIDATION_ENV_02_BOARDROOM.png")
        render_check(os.path.join(C.P["scenes"], C.SCENES["BOARDROOM"]), out)
        print("VALIDATION_RENDER", out, os.path.exists(out))
