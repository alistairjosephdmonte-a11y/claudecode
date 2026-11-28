"""Builds POLYCAB_GLISS_02_MASTER.blend for "Nothing Changed. Everything Did." (15 s, 10 shots, 360 frames @ 24 fps).

    blender -b --factory-startup --python scripts/build_gliss02.py

Reuses the Concept 01 Gliss product master (polycab_gliss/scripts/gliss_product.py) and its material, fixture and
camera-rig helpers (polycab_gliss/scripts/build_gliss.py, imported as G).

Scenes
  SCENE_ARCHITECTURE   shots 1-9: ENV_GLISS_02 living room, three installed Gliss, seated character proxies.
                       View layers BEAUTY (clean plates, proxies excluded) and PREVIS (proxies visible).
  STUDIO_PACKSHOT      shot 10 and the product macro still.
  SCENE_WALKTHROUGH    10 s technical walkthrough: same room, all three Gliss on, no characters.
  SCENE_MASTER_EDIT    VSE assembly, 360 frames, one strip per shot.

Coordinates: origin at the centre of the gallery wall on the finished floor, +Y into the room, +Z up (as the brief).
The brief's X values are MIRRORED (x -> -x). With +Y into the room and Z up, a right-handed frame puts +X on the
viewer's LEFT when facing the wall; the brief's names (GLISS_LEFT, left-side glazing, wedding photograph first on
the left in STORYBOARD_02 and TRANSFORM_02) only work if the brief's +X is the viewer's right. Every brief X
coordinate below is written as MX(value) so the mapping is explicit."""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "polycab_gliss", "scripts"))
sys.path.insert(0, os.path.join(REPO, "polycab_superior_switch", "scripts"))
import build_gliss as G     # noqa: E402
import build_scene as B     # noqa: E402
import gliss_product as GP  # noqa: E402

OUT_BLEND = os.environ.get("GLISS02_OUT") or os.path.join(ROOT, "scenes", "POLYCAB_GLISS_02_MASTER.blend")
FPS = 24
STUDIO_WASH_W = float(os.environ.get("GLISS02_WASH", "230"))


def MX(x):
    return -x


CEIL = 3.0
RX0, RX1, RY0, RY1 = -3.25, 3.25, 0.0, 5.8          # 6.5 x 5.8 x 3.0 m
GLAZ_X = RX1                                         # brief "left side" glazing (viewer's left = +X)
JOIN_X = RX0                                         # brief "right side" walnut joinery
ART_Y, ART_Z = 0.04, 1.6
ARTWORKS = [("MEMORY_01", MX(-1.1), "FEM_01 and MAL_01 at their wedding"),
            ("MEMORY_02", MX(0.0), "A cherished travel memory"),
            ("MEMORY_03", MX(1.1), "FEM_01 and MAL_01 together during a relaxed holiday")]
FIXTURES = [("GLISS_LEFT", (MX(-1.1), 0.9, CEIL), (MX(-1.1), ART_Y, ART_Z), 85),
            ("GLISS_CENTRE", (MX(0.0), 0.9, CEIL), (MX(0.0), ART_Y, ART_Z), 109),
            ("GLISS_RIGHT", (MX(1.1), 0.9, CEIL), (MX(1.1), ART_Y, ART_Z), 127)]
SOFA_C, SOFA_DIM = (0.0, 3.6), (2.7, 0.95, 0.82)
# brief seats +/-0.43 m; moved to +/-0.30 so FEM_01 can physically rest her head on MAL_01's shoulder (shot 07)
FEM_X, MAL_X, SEAT_Y = MX(-0.30), MX(0.30), 3.54
SHOTS = [  # id, scene, first, last, marker
    ("CAM_01_ORDINARY_EVENING", "SCENE_ARCHITECTURE", 1, 36, "01_THE_ORDINARY_EVENING"),
    ("CAM_02_UNNOTICED_MEMORIES", "SCENE_ARCHITECTURE", 37, 60, "02_UNNOTICED_MEMORIES"),
    ("CAM_03_INTRODUCING_GLISS", "SCENE_ARCHITECTURE", 61, 84, "03_INTRODUCING_GLISS"),
    ("CAM_04_FIRST_MEMORY", "SCENE_ARCHITECTURE", 85, 108, "04_THE_FIRST_MEMORY"),
    ("CAM_05_GALLERY_TRANSFORMS", "SCENE_ARCHITECTURE", 109, 144, "05_THE_GALLERY_TRANSFORMS"),
    ("CAM_06_THE_DISCOVERY", "SCENE_ARCHITECTURE", 145, 168, "06_THE_DISCOVERY"),
    ("CAM_07_THE_FEELING", "SCENE_ARCHITECTURE", 169, 204, "07_THE_FEELING"),
    ("CAM_08_NOTHING_CHANGED", "SCENE_ARCHITECTURE", 205, 228, "08_NOTHING_CHANGED"),
    ("CAM_09_EVERYTHING_DID", "SCENE_ARCHITECTURE", 229, 276, "09_EVERYTHING_DID"),
    ("CAM_10_GLAM_UP_YOUR_MEMORIES", "STUDIO_PACKSHOT", 277, 360, "10_GLAM_UP_YOUR_MEMORIES"),
]
G.GLISS_PREVIEW.update(beam_angle_deg=36.0, beam_blend=0.6, light_output_w=70.0, cct_k=3000)
G.COLL_ALIAS.clear()
G.COLL_ALIAS["02_INTERIOR_ASSETS"] = "03_LIFESTYLE_PROPS"     # B.plant() files into this name
M = G.M
coll, link, constant, ease = G.coll, G.link, G.constant, G.ease


# ---------------------------------------------------------------- materials
def build_materials():
    G.build_materials()
    M["OakWarm"] = B.mat_wood("MAT_OAK_NATURAL_WARM", (0.20, 0.12, 0.065), (0.42, 0.28, 0.16), 0.48, axis="Y",
                              stretch=0.1, plank=(1.8, 0.19), coat=0.08)
    M["PlasterWarm"] = B.mat_plain("MAT_PLASTER_WARM_NEUTRAL", (0.66, 0.62, 0.56), rough=0.92, spec=0.3)
    M["Linen"] = B.mat_fabric("MAT_LINEN_IVORY_TEXTURED", (0.70, 0.66, 0.58), rough=0.92, sheen=0.5, scale=700)
    M["Olive"] = B.mat_fabric("MAT_CUSHION_OLIVE_TEXTURED", (0.17, 0.17, 0.07), scale=420)
    M["Throw"] = B.mat_fabric("MAT_THROW_LINEN_OAT", (0.62, 0.55, 0.44), scale=260)
    M["Rug"] = B.mat_fabric("MAT_RUG_WOVEN_WOOL_NEUTRAL", (0.50, 0.46, 0.40), 1.0, 0.5, 300.0)
    M["Curtain"] = B.mat_fabric("MAT_CURTAIN_LINEN_NATURAL", (0.62, 0.57, 0.49), scale=650)
    M["Mat"] = B.mat_plain("MAT_PHOTO_MAT_IVORY", (0.78, 0.75, 0.68), rough=0.95, spec=0.2)
    M["Flower"] = B.mat_plain("MAT_FLOWER_CREAM", (0.80, 0.76, 0.62), rough=0.6, sss=0.15)
    M["ArtGlass"] = mat_ar_glass("MAT_PHOTO_GLAZING_LOW_REFLECTION")
    for mid, *_ in ARTWORKS:
        M[mid] = mat_photo("MAT_" + mid, os.path.join(ROOT, "reference", mid + "_PLACEHOLDER.png"), mid)
    # character proxy wardrobe (flat tints; proxies are blocking aids, not characters)
    for key, name, col in (("FemTop", "MAT_PROXY_FEM_IVORY_BLOUSE", (0.70, 0.66, 0.58)),
                           ("FemLeg", "MAT_PROXY_FEM_BEIGE_TROUSERS", (0.52, 0.44, 0.34)),
                           ("MalTop", "MAT_PROXY_MAL_CHARCOAL_SHIRT", (0.07, 0.07, 0.075)),
                           ("MalLeg", "MAT_PROXY_MAL_TAUPE_TROUSERS", (0.30, 0.26, 0.21)),
                           ("Skin", "MAT_PROXY_SKIN_NEUTRAL", (0.36, 0.25, 0.19)),
                           ("Hair", "MAT_PROXY_HAIR_DARK", (0.02, 0.016, 0.014))):
        M[key] = B.mat_plain(name, col, rough=0.75)
    M["Studio"] = G.mat_studio_backdrop("MAT_STUDIO_CHARCOAL_WALNUT")


def mat_photo(name, path, mid):
    m, n, l, b = B._mat(name)
    img = bpy.data.images.load(path, check_existing=True)
    img.name = mid + "_PLACEHOLDER"
    tx = n.new("ShaderNodeTexImage")
    tx.image = img
    tc = n.new("ShaderNodeTexCoord")
    l.new(tc.outputs["UV"], tx.inputs["Vector"])
    l.new(tx.outputs["Color"], b.inputs["Base Color"])
    B._set(b, rough=0.55, spec=0.3)                      # matte fibre-based print behind glazing
    return m


def mat_ar_glass(name):
    """Low-reflection picture glazing: transparent with a weak Fresnel glossy layer; shadow and diffuse rays pass
    straight through so the Gliss spot reaches the print (Cycles otherwise blocks shadow rays at refractive glass)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.remove(n["Principled BSDF"])
    tr = n.new("ShaderNodeBsdfTransparent")
    gl = n.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    fr = n.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.22              # ~1 % normal reflectance, AR-coated museum glass
    mix = n.new("ShaderNodeMixShader")
    l.new(fr.outputs[0], mix.inputs["Fac"])
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(gl.outputs[0], mix.inputs[2])
    lp = n.new("ShaderNodeLightPath")
    mx = n.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    l.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    l.new(lp.outputs["Is Diffuse Ray"], mx.inputs[1])
    mix2 = n.new("ShaderNodeMixShader")
    l.new(mx.outputs[0], mix2.inputs["Fac"])
    l.new(mix.outputs[0], mix2.inputs[1])
    l.new(tr.outputs[0], mix2.inputs[2])
    l.new(mix2.outputs[0], n["Material Output"].inputs["Surface"])
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m


# ---------------------------------------------------------------- architecture
def build_architecture():
    c = "01_ARCHITECTURE"
    coll(c)
    t = 0.2
    WY0, WY1 = 0.30, 5.50
    B.box("ARCH_Floor_Subfloor", RX0 - t, RX1 + t, RY0 - t, RY1 + t, -0.12, -0.02, M["CeramicDark"], c)
    k = 0
    x = RX0
    col = 0
    while x < RX1 - 1e-6:                            # oak planks 190 x 1800, staggered, running along Y
        x1 = min(x + 0.19, RX1)
        y = RY0 - (0.6 * (col % 3))
        while y < RY1 - 1e-6:
            y0, y1 = max(y, RY0), min(y + 1.8, RY1)
            if y1 - y0 > 0.02:
                B.box("ARCH_Floor_Oak_Plank_%03d" % k, x + 0.0008, x1 - 0.0008, y0 + 0.0008, y1 - 0.0008, -0.02,
                      0.0, M["OakWarm"], c, bev=0.0015, seg=1)
                k += 1
            y += 1.8
        x = x1
        col += 1
    B.box("ARCH_Floor_Joint_Fill", RX0, RX1, RY0, RY1, -0.021, -0.0185, M["CeramicDark"], c)
    # walls 200 mm; gallery wall structure behind the 20 mm travertine cladding
    B.box("ARCH_Wall_Gallery_Structure", RX0 - t, RX1 + t, RY0 - 0.02 - t, RY0 - 0.02, 0, CEIL + 0.2,
          M["PlasterWarm"], c)
    B.box("ARCH_Wall_Front", RX0 - t, RX1 + t, RY1, RY1 + t, 0, CEIL + 0.2, M["PlasterWarm"], c)
    B.box("ARCH_Wall_Joinery_Side", RX0 - t, RX0, RY0 - 0.02, RY1, 0, CEIL + 0.2, M["PlasterWarm"], c)
    B.box("ARCH_Wall_Glazing_Pier_A", RX1, RX1 + t, RY0 - 0.02, WY0, 0, CEIL + 0.2, M["PlasterWarm"], c)
    B.box("ARCH_Wall_Glazing_Pier_B", RX1, RX1 + t, WY1, RY1, 0, CEIL + 0.2, M["PlasterWarm"], c)
    B.box("ARCH_Ceiling_Plaster", RX0 - t, RX1 + t, RY0 - t, RY1 + t, CEIL, CEIL + 0.12, M["PlasterWarm"], c)
    for nm, a in (("Front", (RX0, RX1, RY1 - 0.012, RY1)), ("Joinery_Side", (RX0, RX0 + 0.012, 3.3, RY1)),
                  ("Gallery_L", (2.4, RX1, RY0, RY0 + 0.012)), ("Gallery_R", (RX0, -2.4, RY0, RY0 + 0.012))):
        B.box("ARCH_Skirting_" + nm, *a, 0, 0.08, M["Walnut"], c)
    # floor-to-ceiling glazing on the viewer's left (+X), slim bronze mullions
    B.box("ARCH_Glazing_Glass", GLAZ_X + 0.08, GLAZ_X + 0.09, WY0, WY1, 0.0, CEIL, M["Glazing"], c)
    for i in range(5):
        y = WY0 + (WY1 - WY0) * i / 4
        B.box("ARCH_Glazing_Mullion_%d" % i, GLAZ_X + 0.04, GLAZ_X + 0.12, y - 0.025, y + 0.025, 0.0, CEIL,
              M["Mullion"], c)
    B.box("ARCH_Glazing_Sill", GLAZ_X, GLAZ_X + 0.12, WY0, WY1, 0.0, 0.03, M["Mullion"], c)
    B.box("ARCH_Glazing_Head", GLAZ_X, GLAZ_X + 0.12, WY0, WY1, CEIL - 0.04, CEIL, M["Mullion"], c)
    # gallery wall: honed ivory travertine, 1200 x 600 slabs, 3 mm joints, 4.8 m wide x 3.0 m
    tx0, tx1 = -2.4, 2.4
    B.box("ARCH_Gallery_Wall_Setting_Bed", tx0, tx1, RY0 - 0.02, RY0 - 0.018, 0, CEIL, M["CeramicDark"], c)
    k = 0
    for row in range(int(math.ceil(CEIL / 0.6))):
        z0, z1 = row * 0.6, min((row + 1) * 0.6, CEIL)
        off = 0.6 if row % 2 else 0.0
        xs = tx0 - off
        while xs < tx1 - 1e-6:
            a, b_ = max(xs, tx0), min(xs + 1.2, tx1)
            if b_ - a > 0.02:
                B.box("ARCH_Travertine_Slab_%03d" % k, a + 0.0015, b_ - 0.0015, RY0 - 0.018, RY0, z0 + 0.0015,
                      z1 - 0.0015, M["Travertine"], c, bev=0.001, seg=1)
                k += 1
            xs += 1.2
    # linen curtains stacked open at both ends of the glazing
    for i, (ya, yb) in enumerate(((WY0 + 0.02, WY0 + 0.62), (WY1 - 0.62, WY1 - 0.02))):
        bm = bmesh.new()
        cols = 40
        rows = []
        for zi, z in enumerate((0.012, CEIL - 0.06)):
            rows.append([bm.verts.new((GLAZ_X - 0.10 + 0.035 * math.sin(j / cols * math.pi * 14 + i),
                                       ya + (yb - ya) * j / cols, z)) for j in range(cols + 1)])
        for j in range(cols):
            bm.faces.new((rows[0][j], rows[0][j + 1], rows[1][j + 1], rows[1][j]))
        ob = B.mesh_obj("ARCH_Curtain_Linen_%d" % i, bm, c, M["Curtain"], True)
        sol = ob.modifiers.new("Solidify", "SOLIDIFY")
        sol.thickness = 0.004
    B.box("ARCH_Curtain_Track", GLAZ_X - 0.14, GLAZ_X - 0.06, WY0, WY1, CEIL - 0.04, CEIL, M["PlasterWarm"], c)
    # exterior (constant): blue-hour sky, metropolitan towers and low-rise city plane beyond the +X glazing
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((700, -800, -60), (700, 800, -60), (700, 800, 500), (700, -800, 500))]
    bm.faces.new(vs[::-1])
    sky = B.mesh_obj("EXT_Sky_Backdrop", bm, c, M["Skyline"])
    sky.visible_shadow = False
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((30, -800, -40), (690, -800, -40), (690, 800, -40), (30, 800, -40))]
    bm.faces.new(vs)
    gnd = B.mesh_obj("EXT_City_Ground", bm, c, M["CityGround"])
    gnd.visible_shadow = False
    rnd = 0.53
    for i in range(34):
        rnd = (rnd * 9301 + 49297) % 233280 / 233280.0
        dist = 220 + 380 * ((i * 0.618) % 1.0)
        y = 2.9 + math.tan(math.radians(-50 + 100 * (i + 0.5 * rnd) / 34.0)) * dist
        w = 12 + 14 * rnd
        h = 20 + 100 * ((i * 0.37 + rnd) % 1.0) ** 2
        B.box("EXT_Tower_%02d" % i, dist, dist + w, y, y + w * 0.8, -40, h, M["Tower"], c)


def build_joinery():
    """Walnut joinery and understated shelving on the viewer's right (-X side wall), y 1.0-3.2."""
    c = "02_FURNITURE"
    coll(c)
    x0, x1, y0, y1 = JOIN_X, JOIN_X + 0.40, 1.0, 3.2
    B.box("JOIN_Back_Panel", x0, x0 + 0.02, y0, y1, 0, CEIL, M["WalnutV"], c)
    for i, y in enumerate((y0, y1 - 0.03)):
        B.box("JOIN_Side_%d" % i, x0, x1, y, y + 0.03, 0, CEIL, M["WalnutV"], c, bev=0.002)
    B.box("JOIN_Base_Cabinet", x0 + 0.02, x1, y0 + 0.03, y1 - 0.03, 0, 0.62, M["Walnut"], c, bev=0.002)
    B.box("JOIN_Base_Shadow_Gap", x1 - 0.001, x1 + 0.004, y0 + 0.03, y1 - 0.03, 0.30, 0.306, M["CeramicDark"], c)
    for i, z in enumerate((1.12, 1.58, 2.04, 2.50)):
        B.box("JOIN_Shelf_%d" % i, x0 + 0.02, x1 - 0.01, y0 + 0.03, y1 - 0.03, z, z + 0.035, M["Walnut"], c,
              bev=0.002)
    B.box("JOIN_Top", x0, x1, y0, y1, CEIL - 0.03, CEIL, M["Walnut"], c)
    p = "03_LIFESTYLE_PROPS"
    coll(p)
    for i in range(7):
        B.box("PROP_Shelf_Book_%d" % i, x0 + 0.06, x0 + 0.27 + 0.02 * (i % 3), 1.35 + 0.032 * i, 1.377 + 0.032 * i,
              1.155, 1.155 + 0.21 + 0.02 * (i % 3), M["Book1" if i % 2 else "Book2"], p, bev=0.001)
    for i in range(3):
        B.box("PROP_Shelf_Book_Stack_%d" % i, x0 + 0.08, x0 + 0.30, 2.55, 2.80 - 0.02 * i, 2.075 + 0.03 * i,
              2.103 + 0.03 * i, M["Book2" if i % 2 else "Book1"], p, bev=0.001)
    B.lathe("PROP_Shelf_Vase", [(0, 0), (0.06, 0), (0.09, 0.14), (0.05, 0.3), (0, 0.3)], M["Ceramic"], p,
            loc=(x0 + 0.2, 2.75, 1.155))
    B.lathe("PROP_Shelf_Bowl", [(0, 0), (0.05, 0), (0.12, 0.07), (0.11, 0.075), (0, 0.01)], M["CeramicDark"], p,
            loc=(x0 + 0.2, 1.7, 2.075))
    B.lathe("PROP_Shelf_Ceramic_Tall", [(0, 0), (0.04, 0), (0.07, 0.12), (0.03, 0.26), (0, 0.27)], M["Ceramic"],
            p, loc=(x0 + 0.2, 1.5, 2.535))
    # ceramic table lamp on the base cabinet (existing warm ambience)
    lx, ly = x0 + 0.2, 2.65
    B.lathe("FIX_Joinery_Lamp_Base", [(0, 0), (0.07, 0), (0.09, 0.12), (0.03, 0.26), (0, 0.27)],
            M["CeramicDark"], "07_AMBIENT_LIGHTING", loc=(lx, ly, 0.62))
    B.lathe("FIX_Joinery_Lamp_Shade", [(0.11, 0.86), (0.13, 0.86), (0.10, 1.06), (0.08, 1.06)], M["Shade"],
            "07_AMBIENT_LIGHTING", loc=(lx, ly, 0), smooth=True)
    B.light("LGT_AMBIENT_JOINERY_LAMP", "POINT", (lx, ly, 0.95), 14.0, "07_AMBIENT_LIGHTING", k=2700, size=0.05)


def build_furniture():
    c = "02_FURNITURE"
    coll(c)
    sx, sy = SOFA_C
    L, D, H = SOFA_DIM
    x0, x1, y0, y1 = sx - L / 2, sx + L / 2, sy - D / 2, sy + D / 2      # seat faces -Y (the gallery wall)
    B.box("SOFA_MAIN_Plinth", x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, 0.0, 0.08, M["Walnut"], c)
    B.box("SOFA_MAIN_Seat_Base", x0, x1, y0, y1, 0.08, 0.30, M["Linen"], c, bev=0.03, seg=3)
    B.box("SOFA_MAIN_Back", x0, x1, y1 - 0.24, y1, 0.30, H, M["Linen"], c, bev=0.05, seg=4)
    B.box("SOFA_MAIN_Arm_L", x1 - 0.2, x1, y0, y1 - 0.24, 0.30, 0.62, M["Linen"], c, bev=0.05, seg=4)
    B.box("SOFA_MAIN_Arm_R", x0, x0 + 0.2, y0, y1 - 0.24, 0.30, 0.62, M["Linen"], c, bev=0.05, seg=4)
    w = (L - 0.4) / 3
    for i in range(3):
        a, b_ = x0 + 0.2 + i * w, x0 + 0.2 + (i + 1) * w
        sc = B.box("SOFA_MAIN_Seat_Cushion_%d" % i, a + 0.006, b_ - 0.006, y0 + 0.02, y1 - 0.25, 0.30, 0.44,
                   M["Linen"], c, bev=0.045, seg=4)
        bc = B.box("SOFA_MAIN_Back_Cushion_%d" % i, a + 0.01, b_ - 0.01, y1 - 0.42, y1 - 0.24, 0.44, 0.78,
                   M["Linen"], c, bev=0.06, seg=4)
        bc.rotation_euler = (math.radians(-6), 0, 0)
        for ob, amp in ((sc, 0.006), (bc, 0.004)):          # natural compression unevenness
            tex = bpy.data.textures.new(ob.name + "_Wrinkle", "CLOUDS")
            tex.noise_scale = 0.18
            d = ob.modifiers.new("Wrinkle", "DISPLACE")
            d.texture = tex
            d.strength = amp
            d.mid_level = 0.5
    # coffee table, rug
    tx, ty = 0.0, 2.15
    B.cyl("TABLE_COFFEE_Top", 0.45, 0.31, 0.35, M["Walnut"], c, loc=(tx, ty), n=128, bev=0.006)
    B.cyl("TABLE_COFFEE_Plinth", 0.30, 0.008, 0.31, M["Walnut"], c, loc=(tx, ty), n=96, bev=0.004)
    B.box("RUG_Woven_Wool", -1.6, 1.6, 1.6, 4.2, 0.0, 0.008, M["Rug"], c, bev=0.002, seg=1)
    # floor lamp at the glazing end of the sofa (existing ambient light)
    lx, ly = MX(-1.8), 4.30
    a = "07_AMBIENT_LIGHTING"
    B.cyl("FIX_FloorLamp_Base", 0.15, 0.0, 0.02, M["Bronze"], a, loc=(lx, ly), n=48)
    B.cyl("FIX_FloorLamp_Stem", 0.01, 0.02, 1.45, M["Bronze"], a, loc=(lx, ly), n=16)
    B.lathe("FIX_FloorLamp_Shade", [(0.16, 1.32), (0.20, 1.32), (0.17, 1.62), (0.13, 1.62)], M["Shade"], a,
            loc=(lx, ly, 0), smooth=True)
    B.light("LGT_AMBIENT_FLOORLAMP", "POINT", (lx, ly, 1.48), 45.0, a, k=2700, size=0.08)


def build_props():
    c = "03_LIFESTYLE_PROPS"
    coll(c)
    sx, sy = SOFA_C
    L, D, H = SOFA_DIM
    # two textured sofa cushions + one casually draped throw
    for nm, x, mat, rz in (("PROP_Cushion_Olive", MX(-1.02), M["Olive"], 12), ("PROP_Cushion_Ivory", MX(1.0),
                                                                                M["Linen"], -9)):
        ob = B.box(nm, x - 0.22, x + 0.22, sy + 0.08, sy + 0.22, 0.46, 0.90, mat, c, bev=0.06, seg=4)
        ob.rotation_euler = (math.radians(-14), math.radians(rz * 0.3), math.radians(rz))
        ob.location = (0, 0, 0)
    bm = bmesh.new()                                  # throw: over the +X arm, hanging to the outside
    ax = sx + L / 2
    prof = [(ax - 0.30, 0.445), (ax - 0.18, 0.47), (ax - 0.10, 0.60), (ax - 0.02, 0.635), (ax + 0.04, 0.60),
            (ax + 0.07, 0.40), (ax + 0.09, 0.18)]
    rows = []
    for yi in range(9):
        y = sy - 0.30 + 0.06 * yi
        rows.append([bm.verts.new((px + 0.01 * math.sin(yi * 1.7 + j), y, pz + 0.008 * math.sin(yi * 2.3 + j * 0.7)))
                     for j, (px, pz) in enumerate(prof)])
    for yi in range(8):
        for j in range(len(prof) - 1):
            bm.faces.new((rows[yi][j], rows[yi][j + 1], rows[yi + 1][j + 1], rows[yi + 1][j]))
    ob = B.mesh_obj("PROP_Throw_Linen", bm, c, M["Throw"], True)
    sol = ob.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = 0.008
    sub = ob.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = sub.render_levels = 1
    # coffee table: cream flowers in a ceramic vase, two books, a small ceramic object
    tx, ty, tz = 0.0, 2.15, 0.35
    vx, vy = tx + MX(0.16), ty - 0.08
    B.lathe("PROP_Flower_Vase_Ceramic", [(0, 0), (0.06, 0), (0.08, 0.10), (0.045, 0.22), (0.05, 0.24),
                                         (0, 0.24)], M["Ceramic"], c, loc=(vx, vy, tz))
    for i in range(14):
        a = i * 2.399
        r = 0.035 + 0.075 * ((i * 0.618) % 1)
        p = (vx + r * math.cos(a), vy + r * math.sin(a), tz + 0.42 + 0.1 * ((i * 0.37) % 1) - 0.6 * r)
        B.cyl("PROP_Flower_Stem_%02d" % i, 0.0025, tz + 0.2, p[2], M["Foliage"], c, loc=(vx + 0.3 * (p[0] - vx),
                                                                                       vy + 0.3 * (p[1] - vy)), n=6)
        B.sphere("PROP_Flower_Bloom_%02d" % i, 0.032, p, M["Flower"], c, scale=(1, 1, 0.75))
    for i in range(2):
        bx, by = tx + MX(-0.14), ty + 0.10
        B.box("PROP_Table_Book_%d" % i, bx - 0.13 + 0.01 * i, bx + 0.11 - 0.01 * i, by - 0.09, by + 0.09 - 0.01 * i,
              tz + 0.024 * i, tz + 0.023 + 0.024 * i, M["Book1" if i else "Book2"], c, bev=0.001)
    B.lathe("PROP_Table_Ceramic_Object", [(0, 0), (0.035, 0), (0.055, 0.04), (0.04, 0.09), (0.012, 0.11),
                                          (0, 0.11)], M["CeramicDark"], c, loc=(tx + MX(-0.12), ty + 0.10, tz + 0.047))
    B.plant("PROP_Indoor_Plant", (MX(2.72), 0.52, 0.0), 0.22, 1.55)


def build_gallery():
    c = "04_GALLERY_ARTWORK"
    coll(c)
    W, H, fw, fd = 0.70, 0.90, 0.035, 0.045
    P = 0.46                                           # square photograph window in the ivory mat
    for mid, x, content in ARTWORKS:
        z = ART_Z
        for nm, (a0, a1, b0, b1) in (("T", (x - W / 2, x + W / 2, z + H / 2 - fw, z + H / 2)),
                                     ("B", (x - W / 2, x + W / 2, z - H / 2, z - H / 2 + fw)),
                                     ("L", (x - W / 2, x - W / 2 + fw, z - H / 2 + fw, z + H / 2 - fw)),
                                     ("R", (x + W / 2 - fw, x + W / 2, z - H / 2 + fw, z + H / 2 - fw))):
            B.box("%s_Frame_%s" % (mid, nm), a0, a1, RY0 + 0.002, RY0 + fd, b0, b1, M["Walnut"], c, bev=0.002)
        B.box(mid + "_Backing", x - W / 2 + 0.01, x + W / 2 - 0.01, RY0 + 0.002, RY0 + 0.012, z - H / 2 + 0.01,
              z + H / 2 - 0.01, M["CeramicDark"], c)
        # mat board with the photograph window (four strips) and the print behind it
        mz0, mz1, mx0, mx1 = z - H / 2 + fw, z + H / 2 - fw, x - W / 2 + fw, x + W / 2 - fw
        for nm, (a0, a1, b0, b1) in (("T", (mx0, mx1, z + P / 2, mz1)), ("B", (mx0, mx1, mz0, z - P / 2)),
                                     ("L", (mx0, x - P / 2, z - P / 2, z + P / 2)),
                                     ("R", (x + P / 2, mx1, z - P / 2, z + P / 2))):
            B.box("%s_Mat_%s" % (mid, nm), a0, a1, RY0 + 0.026, RY0 + 0.030, b0, b1, M["Mat"], c)
        bm = bmesh.new()
        yp = RY0 + 0.024
        v = [bm.verts.new((x + sx * P / 2, yp, z + sz * P / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = bm.faces.new((v[3], v[2], v[1], v[0]))
        uv = bm.loops.layers.uv.new()
        for loop in f.loops:
            co = loop.vert.co
            # viewed from +Y the viewer's right is -X, so u runs from +X (left) to -X (right)
            loop[uv].uv = (((x + P / 2) - co.x) / P, (co.z - (z - P / 2)) / P)
        ph = B.mesh_obj(mid + "_Photograph", bm, c, M[mid])
        ph["content"] = content
        ph["image_status"] = ("ANIMATIC PLACEHOLDER: crop of the PROP_GLISS_02 reference sheet (~130 px source, "
                              "generated imagery). Replace with the approved photograph. Static in every shot.")
        g = B.box(mid + "_Glazing", mx0, mx1, RY0 + 0.036, RY0 + 0.038, mz0, mz1, M["ArtGlass"], c)
        g.visible_shadow = False
        ctr = B.empty(mid + "_CENTRE", (x, ART_Y, z), c, "SPHERE", 0.02)
        ctr["brief_position"] = [MX(x), ART_Y, z]


def build_ambient():
    c = "07_AMBIENT_LIGHTING"
    coll(c)
    lt = B.light("LGT_AMBIENT_CEILING_BOUNCE", "AREA", (0.0, 3.2, CEIL - 0.02), 45.0, c, k=2900, size=4.0,
                 size_y=3.0)
    lt.visible_camera = lt.visible_glossy = False
    pt = B.light("LGT_WINDOW_PORTAL", "AREA", (GLAZ_X + 0.1, 2.9, CEIL / 2), 0.0, c, size=CEIL, size_y=5.2,
                 rot=(0, math.radians(90), 0))
    pt.data.cycles.is_portal = True


def build_fixtures(sc, cname, prefix="", always_on=False):
    G._TARGET["scene"] = sc
    coll(cname)
    out = []
    for name, loc, tgt, f_on in FIXTURES:
        keys = ((1, 1.0),) if always_on else ((1, 0.0), (f_on, 1.0))
        mi, hi, sp = G.fixture(prefix + name, loc, cname, target=tgt, on_keys=keys)
        mi["illumination_target_m"] = tgt
        mi["brief_mount_position_m"] = [MX(loc[0]), loc[1], loc[2]]
        mi["orientation_status"] = "PROVISIONAL until verified articulation limits are available"
        out.append((mi, hi, sp))
    return out


# ---------------------------------------------------------------- character proxies
def ellip(name, p0, p1, rx, ry, mat, c, parent):
    """Ellipsoid spanning p0-p1 (parent-local), radii rx/ry across. Mesh lives in the parent's frame."""
    p0, p1 = Vector(p0), Vector(p1)
    ax = p1 - p0
    half = max(ax.length / 2, 1e-4)
    q = ax.normalized().to_track_quat("Z", "Y") if ax.length > 1e-6 else Euler().to_quaternion()
    mat4 = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((rx, ry, half + rx * 0.5,
                                                                                         1.0))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=1.0)
    bmesh.ops.transform(bm, matrix=mat4, verts=bm.verts)
    ob = B.mesh_obj(name, bm, c, mat, True)
    ob.parent = parent
    return ob


def seated_proxy(pid, x, height, top, leg, hair_long, hip_z):
    c = "09_CHARACTER_PROXIES"
    coll(c)
    s = height / 1.70
    root = B.empty(pid + "_PROXY_ROOT", (x, SEAT_Y, hip_z), c, "SINGLE_ARROW", 0.2)
    root["proxy_note"] = ("Correctly scaled blocking proxy (%.2f m standing). Not a character: final performances "
                          "come from reference-guided generation on the clean plates, or approved digital doubles."
                          % height)
    for sx in (-1, 1):
        k = (sx * 0.10 * s, -0.45 * s, 0.0)
        ellip("%s_Thigh_%s" % (pid, "L" if sx > 0 else "R"), (sx * 0.09 * s, 0, 0.0), k, 0.075 * s, 0.075 * s,
              M[leg], c, root)
        an = (sx * 0.10 * s, -0.50 * s, -0.43 * root.location.z / 0.52)
        ellip("%s_Shin_%s" % (pid, "L" if sx > 0 else "R"), k, an, 0.055 * s, 0.055 * s, M[leg], c, root)
        ellip("%s_Foot_%s" % (pid, "L" if sx > 0 else "R"), (an[0], an[1] + 0.03, an[2] - 0.04),
              (an[0], an[1] - 0.17 * s, an[2] - 0.05), 0.045 * s, 0.04 * s, M["Hair"], c, root)
    ellip(pid + "_Pelvis", (-0.11 * s, 0.0, 0.03), (0.11 * s, 0.0, 0.03), 0.11 * s, 0.10 * s, M[leg], c, root)
    tp = B.empty(pid + "_TORSO_PIVOT", (0, 0, 0), c, "ARROWS", 0.1)
    tp.parent = root
    tp.rotation_euler = (math.radians(-8), 0, 0)          # slight recline into the back cushions
    ellip(pid + "_Torso", (0, 0, 0.10 * s), (0, 0.0, 0.48 * s), 0.17 * s, 0.11 * s, M[top], c, tp)
    for sx in (-1, 1):
        sh, el, hd = (sx * 0.19 * s, 0.0, 0.45 * s), (sx * 0.22 * s, -0.05 * s, 0.20 * s), \
            (sx * 0.12 * s, -0.33 * s, 0.10 * s)
        ellip("%s_UpperArm_%s" % (pid, "L" if sx > 0 else "R"), sh, el, 0.045 * s, 0.045 * s, M[top], c, tp)
        ellip("%s_Forearm_%s" % (pid, "L" if sx > 0 else "R"), el, hd, 0.035 * s, 0.035 * s, M["Skin"], c, tp)
    ellip(pid + "_Neck", (0, 0, 0.47 * s), (0, 0, 0.58 * s), 0.05 * s, 0.05 * s, M["Skin"], c, tp)
    hp = B.empty(pid + "_HEAD_PIVOT", (0, 0, 0.57 * s), c, "ARROWS", 0.08)
    hp.parent = tp
    ellip(pid + "_Head", (0, 0.0, 0.06 * s), (0, 0.0, 0.24 * s), 0.078 * s, 0.095 * s, M["Skin"], c, hp)
    ellip(pid + "_Hair", (0, 0.012, 0.12 * s) if not hair_long else (0, 0.03, -0.02),
          (0, 0.012, 0.265 * s), 0.084 * s, 0.092 * s, M["Hair"], c, hp)
    ellip(pid + "_Nose_Facing", (0, -0.088 * s, 0.14 * s), (0, -0.10 * s, 0.135 * s), 0.012, 0.012, M["Skin"], c,
          hp)
    eye = B.empty(pid + "_EYES", (0, -0.085 * s, 0.165 * s), c, "SPHERE", 0.01)
    eye.parent = hp
    return root, tp, hp, eye


def build_characters():
    fem = seated_proxy("FEM_01", FEM_X, 1.62, "FemTop", "FemLeg", True, 0.486)
    mal = seated_proxy("MAL_01", MAL_X, 1.78, "MalTop", "MalLeg", False, 0.505)
    bpy.context.view_layer.update()
    # FEM_01 rests her head on MAL_01's shoulder: solve the lean so the head surface meets the shoulder
    froot, ftp, fhp, feye = fem
    mtp = mal[1]
    sm = 1.78 / 1.70
    side = 1 if FEM_X > MAL_X else -1                    # MAL shoulder nearest FEM
    sh_top = mtp.matrix_world @ Vector((side * 0.19 * sm, 0.0, 0.45 * sm + 0.05))
    rhead = 0.078 * (1.62 / 1.70)

    def head_gap(phi):
        ftp.rotation_euler = (math.radians(-8), phi, 0)
        fhp.rotation_euler = (0, phi * 1.4, 0)
        bpy.context.view_layer.update()
        hc = fhp.matrix_world @ Vector((0, 0, 0.15 * 1.62 / 1.70))
        return (hc - sh_top).length - rhead + 0.012

    lo, hi = 0.0, -side * math.radians(40)
    lo_v = head_gap(lo)
    for _ in range(30):
        mid = (lo + hi) / 2
        if (head_gap(mid) > 0) == (lo_v > 0):
            lo = mid
        else:
            hi = mid
    phi = (lo + hi) / 2
    froot["lean_solution_deg"] = math.degrees(phi)
    # animation (constant transforms elsewhere): shot 06 eyes lift to the wall, shot 07 lean in and rest
    for f, tilt in ((1, 9.0), (147, 9.0), (160, 0.0)):
        fhp.rotation_euler = (math.radians(tilt), 0, 0)
        fhp.keyframe_insert("rotation_euler", frame=f)
    for f, p in ((1, 0.0), (172, 0.0), (192, phi)):
        ftp.rotation_euler = (math.radians(-8), p, 0)
        ftp.keyframe_insert("rotation_euler", frame=f)
    for f, p in ((172, 0.0), (192, phi * 1.4)):
        fhp.rotation_euler = (0, p, 0)
        fhp.keyframe_insert("rotation_euler", index=1, frame=f)
    mhp = mal[2]
    for f, yaw in ((1, 0.0), (182, 0.0), (198, 7.0 * (1 if FEM_X > MAL_X else -1))):
        mhp.rotation_euler = (0, 0, math.radians(yaw))
        mhp.keyframe_insert("rotation_euler", index=2, frame=f)
    for ob in (ftp, fhp, mhp):
        ease(ob)
    return fem, mal


# ---------------------------------------------------------------- cameras
def housing_centre(prefix):
    bpy.context.view_layer.update()
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    d = GP.dims_m(json.loads(root["dimension_register_json"]))
    R, L = d["housing_outer_diameter"] / 2, d["housing_length"]
    pr = min(d["pivot_offset"], L * 0.6)
    hi = bpy.data.objects[prefix + "_HEAD"]
    return hi.matrix_world @ Vector((0, -R, (pr - (L - pr)) / 2)), \
        hi.matrix_world @ Vector(root["emitter_head_local_m"])


def build_arch_cameras(arch, fem, mal):
    G._TARGET["scene"] = arch
    c = "10_CINEMATIC_CAMERAS"
    coll(c)
    cams = {}
    p01, t01 = (MX(2.5), 5.3, 1.65), (MX(0.0), 0.2, 1.65)
    cams["01"] = G.cam_rig("CAM_01_ORDINARY_EVENING", c, 24.0, 8.0, [(1, p01, t01), (36, p01, t01)])
    cams["02"] = G.cam_rig("CAM_02_UNNOTICED_MEMORIES", c, 50.0, 5.6,
                           [(37, (MX(-0.5), 2.5, 1.65), (0, ART_Y, ART_Z)), (60, (MX(0.0), 2.5, 1.65),
                                                                            (0, ART_Y, ART_Z))])
    hc, em = housing_centre("GLISS_LEFT")
    p3 = hc + Vector((MX(-0.40), -0.52, -0.66)).normalized() * 1.05
    cams["03"] = G.cam_rig("CAM_03_INTRODUCING_GLISS", c, 85.0, 5.6, [(61, p3, hc), (84, p3, hc)],
                           orbit=(Vector((hc.x, hc.y, p3.z)), -4.0, 4.0, 61, 84),
                           focus_keys=[(61, (hc - p3).length), (84, (hc - p3).length)])
    # brief y 2.1 gives a 0.83 m frame height at 50 mm, smaller than the 0.9 m artwork: moved back to y 2.75
    cams["04"] = G.cam_rig("CAM_04_FIRST_MEMORY", c, 50.0, 5.6,
                           [(85, (MX(-1.1), 2.75, 1.65), (MX(-1.1), ART_Y, ART_Z)),
                            (108, (MX(-1.1), 2.75, 1.65), (MX(-1.1), ART_Y, ART_Z))])
    cams["05"] = G.cam_rig("CAM_05_GALLERY_TRANSFORMS", c, 35.0, 8.0,
                           [(109, (0.0, 3.1, 1.8), (0.0, ART_Y, 1.85)), (144, (0.0, 3.1, 1.8), (0.0, ART_Y, 1.85))])
    arch.frame_set(150)
    eye = fem[3].matrix_world.translation.copy()
    p6a = Vector((FEM_X + MX(-0.48), 1.00, eye.z + 0.03))
    p6b = p6a + (eye - p6a).normalized() * 0.07
    cams["06"] = G.cam_rig("CAM_06_THE_DISCOVERY", c, 85.0, 4.0, [(145, p6a, eye), (168, p6b, eye)],
                           focus_obj=fem[3])
    arch.frame_set(195)
    mid = (fem[2].matrix_world.translation + mal[2].matrix_world.translation) / 2 + Vector((0, 0, 0.02))
    p7a = Vector((MX(0.70), 1.85, mid.z + 0.10))
    p7b = p7a + (mid - p7a).normalized() * 0.02
    cams["07"] = G.cam_rig("CAM_07_THE_FEELING", c, 50.0, 4.0, [(169, p7a, mid), (204, p7b, mid)])
    arch.frame_set(1)
    # CAM_08 IS CAM_01: shared camera data, identity parent transform
    c8 = bpy.data.objects.new("CAM_08_NOTHING_CHANGED", cams["01"].data)
    c8.parent = cams["01"]
    link(c8, c)
    c8["camera_source"] = "Exact duplicate of CAM_01_ORDINARY_EVENING (shared data, identity parent)"
    cams["08"] = c8
    k9 = [(229, (MX(1.65), 3.05, 1.65)), (240, (MX(1.85), 3.55, 1.65)), (252, (MX(2.05), 4.10, 1.65)),
          (264, (MX(2.30), 4.65, 1.65)), (276, (MX(2.50), 5.30, 1.65))]
    cams["09"] = G.cam_rig("CAM_09_EVERYTHING_DID", c, 24.0, 8.0, [(f, p, (0.0, 0.3, 1.65)) for f, p in k9])
    return cams


def build_walkthrough_camera(walk):
    G._TARGET["scene"] = walk
    c = "10_WALKTHROUGH_CAMERA"
    coll(c)
    keys = [(1, (MX(2.5), 5.3, 1.65), (MX(0.0), 0.2, 1.65)), (60, (MX(2.2), 4.4, 1.65), (0.0, ART_Y, 1.65)),
            (120, (MX(1.7), 3.2, 1.65), (0.0, ART_Y, 1.65)), (180, (MX(1.2), 2.4, 1.65), (0.0, ART_Y, 1.65)),
            (240, (MX(0.6), 1.8, 1.65), (0.0, ART_Y, ART_Z))]
    cam = G.cam_rig("CAM_WALKTHROUGH", c, 24.0, 8.0, keys)
    # controlled arc-length timing: re-key so speed is uniform, easing only at the ends
    dolly, tgt = bpy.data.objects["CAM_WALKTHROUGH_DOLLY"], bpy.data.objects["CAM_WALKTHROUGH_TARGET"]
    segs = [(Vector(keys[i + 1][1]) - Vector(keys[i][1])).length for i in range(len(keys) - 1)]
    acc, frames = 0.0, [1]
    for s_ in segs:
        acc += s_
        frames.append(1 + round(239 * acc / sum(segs)))
    for ob in (dolly, tgt):
        ob.animation_data_clear()
    for (_, p, t), f in zip(keys, frames):
        dolly.location = p
        dolly.keyframe_insert("location", frame=f)
        tgt.location = t
        tgt.keyframe_insert("location", frame=f)
    for idb in (dolly, tgt):
        for fc in B.fcurves_of(idb):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO"
            fc.keyframe_points[0].handle_right_type = "AUTO_CLAMPED"
            fc.keyframe_points[-1].handle_left_type = "AUTO_CLAMPED"
            fc.update()
    cd = cam.data
    cd.animation_data_clear()
    for (_, p, t), f in zip(keys, frames):
        cd.dof.focus_distance = (Vector(t) - Vector(p)).length
        cd.dof.keyframe_insert("focus_distance", frame=f)
    ease(cd)
    cam["arc_length_key_frames"] = frames
    walk.camera = cam
    return cam


# ---------------------------------------------------------------- studio
def build_studio(studio):
    G._TARGET["scene"] = studio
    mi, hi = G.build_studio(studio)
    G._TARGET["scene"] = studio
    c = "10_CINEMATIC_CAMERAS"
    coll(c)
    sweep = bpy.data.objects["STUDIO_Sweep"]
    sweep.data.materials[0] = M["Studio"]
    # warm wash on the sweep only (light linking), so the backdrop tone meets the END_02 plate at the join while
    # the product keeps its own key/rim lighting
    rc = bpy.data.collections.new("STUDIO_BACKDROP_RECEIVERS")
    rc.objects.link(sweep)
    for nm, loc, tgt, pw, sz in (("LGT_STUDIO_BACKDROP_WASH", (0.0, -1.2, 1.4), (0.0, 1.6, 1.2), STUDIO_WASH_W, 2.5),
                                 ("LGT_STUDIO_BACKDROP_GLOW", (-0.25, 0.2, 0.75), (-0.1, 1.6, 0.6),
                                  STUDIO_WASH_W * 0.7, 0.6)):
        lt = B.light(nm, "AREA", loc, pw, "11_STUDIO_PACKSHOT", k=4300, size=sz)
        lt.rotation_euler = (Vector(tgt) - lt.location).to_track_quat("-Z", "Y").to_euler()
        lt.visible_camera = False
        lt.light_linking.receiver_collection = rc
    front, emit, centre, axis, R = G.product_points()
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    d = GP.dims_m(json.loads(root["dimension_register_json"]))
    L = d["housing_length"]
    pr = min(d["pivot_offset"], L * 0.6)
    Mx = mi.matrix_basis @ hi.matrix_basis
    pts = [Mx @ Vector((sx * R, -R + sy * R, zz)) for sx in (-1, 1) for sy in (-1, 1) for zz in (pr, -(L - pr))]
    rb = d["mounting_base_diameter"] / 2
    pts += [mi.matrix_basis @ Vector((sx * rb, sy * rb, 0.0)) for sx in (-1, 1) for sy in (-1, 1)]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi_ = Vector([max(p[i] for p in pts) for i in range(3)])
    bc = (lo + hi_) / 2
    pdist = (hi_.z - lo.z) / (0.62 * 20.25 / 85.0) + (hi_.y - lo.y) / 2
    fw = 36.0 / 85.0 * pdist
    look = bc + Vector((fw * (0.5 - 0.225), 0.0, 0.0))     # product centred in the left 45 %
    pk = look + Vector((0.0, -pdist, 0.0))
    cams = {"10": G.cam_rig("CAM_10_GLAM_UP_YOUR_MEMORIES", c, 85.0, 8.0, [(277, pk, look), (360, pk, look)],
                            focus_keys=[(277, (bc - pk).length), (360, (bc - pk).length)])}
    start = emit + axis * 0.205
    cams["macro"] = G.cam_rig("CAM_PRODUCT_MACRO", c, 100.0, 8.0, [(37, start, emit), (60, start, emit)],
                              focus_keys=[(37, (emit - start).length - 0.006)])
    return cams


# ---------------------------------------------------------------- edit, organisation
def build_edit(edit, scenes, cams):
    edit.render.fps = FPS
    edit.frame_start, edit.frame_end = 1, 360
    edit.render.resolution_x, edit.render.resolution_y = 3840, 2160
    se = edit.sequence_editor_create()
    for cid, scn, f0, f1, mk in SHOTS:
        st = se.strips.new_scene(name=mk, scene=scenes[scn], channel=1, frame_start=1)
        st.scene_camera = cams[cid]
        st.frame_final_start = f0
        st.frame_final_end = f1 + 1
        edit.timeline_markers.new(mk, frame=f0)


def reference_collection(arch):
    G._TARGET["scene"] = arch
    c = coll("00_REFERENCE_ASSETS")
    for i, nm in enumerate(("STORYBOARD_02", "PROP_GLISS_02", "ENV_GLISS_02", "TRANSFORM_02", "END_02")):
        img = bpy.data.images.load(os.path.join(ROOT, "reference", nm + ".webp"), check_existing=True)
        e = bpy.data.objects.new("REF_" + nm, None)
        e.empty_display_type = "IMAGE"
        e.data = img
        e.empty_display_size = 1.6
        e.location = (-12.0 + 1.8 * i, 8.0, 1.0)
        e.rotation_euler = (math.radians(90), 0, math.radians(180))
        c.objects.link(e)
    c["note"] = ("Generated reference sheets. Official product imagery and the brief's written corrections "
                 "override them. Empties only; never rendered.")


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    arch = bpy.context.scene
    arch.name = "SCENE_ARCHITECTURE"
    studio = G.scene("STUDIO_PACKSHOT")
    walk = G.scene("SCENE_WALKTHROUGH")
    edit = G.scene("SCENE_MASTER_EDIT")
    G._TARGET["scene"] = arch
    build_materials()
    M["Shade"] = B.MAT.get("Shade")
    G.build_product_master(studio)
    for sc in (arch, walk):
        sc.collection.children.link(bpy.data.collections["01_GLISS_PRODUCT_MASTER"])
        G.exclude(sc.view_layers[0], "01_GLISS_PRODUCT_MASTER")
    G._TARGET["scene"] = studio
    coll("11_STUDIO_PACKSHOT")
    G.COLL_ALIAS["04_PRODUCT_STUDIO"] = "11_STUDIO_PACKSHOT"
    scams = build_studio(studio)
    G._TARGET["scene"] = arch
    reference_collection(arch)
    G._TARGET["scene"] = arch
    for cn in ("01_ARCHITECTURE", "02_FURNITURE", "03_LIFESTYLE_PROPS", "04_GALLERY_ARTWORK"):
        coll(cn)
    build_architecture()
    build_joinery()
    build_furniture()
    build_props()
    build_gallery()
    build_ambient()
    fixtures = build_fixtures(arch, "06_GLISS_INSTANCES")
    # accent spot lights live in their own collection (still parented to their fixture heads)
    acc = coll("08_ACCENT_LIGHTING")
    for _, _, sp in fixtures:
        for cc in list(sp.users_collection):
            cc.objects.unlink(sp)
        acc.objects.link(sp)
    fem, mal = build_characters()
    acams = build_arch_cameras(arch, fem, mal)
    rp = coll("12_RENDER_PASSES")
    rp["note"] = ("Pass configuration lives on the view layers (BEAUTY / PREVIS): combined, depth, normal, vector, "
                  "diffuse and glossy direct/indirect, emission, shadow catcher, Cryptomatte object and material. "
                  "Cycles has no standalone shadow pass since 3.0.")
    # walkthrough shares the room, furniture, props, artwork and ambient light; own always-on fixture set
    for cn in ("01_ARCHITECTURE", "02_FURNITURE", "03_LIFESTYLE_PROPS", "04_GALLERY_ARTWORK", "07_AMBIENT_LIGHTING"):
        walk.collection.children.link(bpy.data.collections[cn])
    build_fixtures(walk, "06_GLISS_INSTANCES_WALKTHROUGH", prefix="WALK_", always_on=True)
    wcam = build_walkthrough_camera(walk)
    G.build_world(arch, "WORLD_BLUE_HOUR", (0.03, 0.06, 0.16), 1.0)
    walk.world = arch.world
    G.build_world(studio, "WORLD_STUDIO_BLACK", (0.004, 0.004, 0.005), 1.0)
    vb = arch.view_layers[0]
    vb.name = "BEAUTY"
    vp = arch.view_layers.new("PREVIS")
    G.exclude(vb, "09_CHARACTER_PROXIES")
    G.exclude(vp, "01_GLISS_PRODUCT_MASTER")
    G.exclude(vp, "00_REFERENCE_ASSETS")
    G.exclude(vb, "00_REFERENCE_ASSETS")
    for sc, fr in ((studio, (1, 360)), (arch, (1, 360)), (walk, (1, 240))):
        G.render_settings(sc, fr)
        sc.cycles.preview_samples = 48
        for vl in sc.view_layers:
            vl.cycles.use_pass_shadow_catcher = True
        sc["exposure_lock"] = "Exposure and white balance locked after calibration (identical in every state)"
    vp.use = False
    cams = {cid: (acams.get(cid[4:6]) or scams.get(cid[4:6])) for cid, *_ in SHOTS}
    G.bind_markers(arch, [(f0, mk, cams[cid]) for cid, scn, f0, f1, mk in SHOTS if scn == "SCENE_ARCHITECTURE"])
    G.bind_markers(studio, [(37, "PRODUCT_MACRO_STILL", scams["macro"]),
                            (277, "10_GLAM_UP_YOUR_MEMORIES", scams["10"])])
    build_edit(edit, {s.name: s for s in (studio, arch)}, cams)
    # organisation: spec collection names; master object id; rebuild code travels with the file
    bpy.data.collections["01_GLISS_PRODUCT_MASTER"].name = "05_GLISS_MASTER"
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    root.name = "GLISS_MASTER_02"
    txt = bpy.data.texts["gliss_product.py"]
    txt.from_string(txt.as_string().replace('"GLISS_MASTER_ROOT"', '"GLISS_MASTER_02"'))
    for o in bpy.data.objects:                        # apply scale on static meshes (no animated scale anywhere)
        if o.type == "MESH" and o.parent is None and not o.animation_data and tuple(o.scale) != (1, 1, 1):
            o.data = o.data.copy() if o.data.users > 1 else o.data
            o.data.transform(Matrix.Diagonal((*o.scale, 1)))
            o.scale = (1, 1, 1)
    for sc in (studio, arch, walk):
        sc.frame_set(1)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    print("SAVED", OUT_BLEND, "objects", len(bpy.data.objects), "lean_deg", fem[0]["lean_solution_deg"])


main()
