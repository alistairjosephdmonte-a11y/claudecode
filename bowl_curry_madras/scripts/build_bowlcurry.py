"""Builds BOWLCURRY_MADRAS_BLOCKOUT.blend for "Ten Minutes to Madras" (15 s, 360 frames @ 24 fps).

    blender -b --factory-startup --python scripts/build_bowlcurry.py

BLOCKOUT STAGE (spec section 07): neutral clay materials everywhere; orange marks the provisional product cartons only.
Every object carries a `final_material` custom property naming the material from the spec, applied after approval.
Units: metres. Origin: apartment floor, south-west corner area; +Y away from the camera side, window wall at x = -4.

Layout
  ENV_BC_01        8.0 x 5.5 x 2.8 m open kitchen/dining; full-height window on the west wall (camera-left for both
                   cameras, which look roughly +Y); kitchen island with flush induction hob; dining table near window.
  BC_MADRAS_01     provisional carton 120 x 45 x 190 mm (W x D x H), bevelled edges, 0.6 mm board shell, dieline UVs
                   ready for the official artwork; one on the island (shots 1-2), one on the dining table (hero).
  PROP_PAN_01      280 mm cast-iron skillet (top inner diameter), 5 mm walls, 6.5 mm base, handle + helper lip.
  FOOD_*           chicken (9 irregular seared-piece proxies), sauce level proxy, spice particles (ballistic keyed
                   proxies), serving bowl + rice.
  FX_STEAM         two procedural volume columns; their density hides the CAM_A -> CAM_B cut (frames 236-246).
  SIM_MANTAFLOW    liquid domain / inflow / collision setup for the sauce pour, NOT baked: viscosity is PROVISIONAL
                   until calibrated against the prepared product (see README).
Cameras  CAM_A frames 1-240 (kitchen), CAM_B 241-360 (dining, hero hold 288-360). Bezier keys, Track-To targets."""

import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "polycab_superior_switch", "scripts"))
import build_scene as B  # noqa: E402  (mesh/material helpers only)

OUT = os.path.join(ROOT, "scenes", "BOWLCURRY_MADRAS_BLOCKOUT.blend")
FPS, F_END, CUT = 24, 360, 241
ISLAND_TOP = 0.91
HOB_TOP = 0.914
PAN_C = Vector((1.95, 3.32, HOB_TOP))
PAN_FLOOR = HOB_TOP + 0.0065
TABLE_TOP = 0.75
CARTON = dict(w=0.120, d=0.045, h=0.190)          # PROVISIONAL (spec), replace with measured values
BOWL_C = Vector((-2.30, 2.58, TABLE_TOP + 0.004))
RICE_C = Vector((-2.36, 2.86, TABLE_TOP + 0.002))
HERO_CARTON = Vector((-2.15, 2.73, TABLE_TOP + 0.002))
ISLAND_CARTON = Vector((1.30, 3.28, ISLAND_TOP))

M = {}


def tag(ob, final):
    ob["final_material"] = final
    return ob


def clay(name, v, rough=0.6, metal=0.0):
    m = B.mat_plain(name, (v, v, v), rough=rough, metal=metal, spec=0.35)
    return m


def build_materials():
    M["arch"] = clay("CLAY_ARCH", 0.62, 0.8)
    M["floor"] = clay("CLAY_FLOOR", 0.50, 0.7)
    M["joinery"] = clay("CLAY_JOINERY", 0.55, 0.7)
    M["stone"] = clay("CLAY_COUNTER", 0.70, 0.55)
    M["metal"] = clay("CLAY_METAL", 0.45, 0.35, 0.6)
    M["hob"] = clay("CLAY_HOB", 0.10, 0.25)
    M["iron"] = clay("CLAY_COOKWARE", 0.20, 0.55)
    M["food"] = clay("CLAY_FOOD", 0.52, 0.65)
    M["sauce"] = clay("CLAY_SAUCE", 0.40, 0.45)
    M["spice"] = clay("CLAY_SPICE", 0.30, 0.8)
    M["ceramic"] = clay("CLAY_TABLEWARE", 0.78, 0.5)
    M["linen"] = clay("CLAY_LINEN", 0.68, 0.9)
    M["carton"] = B.mat_plain("CARTON_PROVISIONAL_ORANGE", (0.85, 0.28, 0.03), rough=0.5, spec=0.4)
    M["glass"] = B.mat_glass("CLAY_GLASS")
    M["steam"] = mat_steam("FX_STEAM_VOLUME")
    M["sky"] = B.mat_plain("CLAY_EXTERIOR", (0.8, 0.8, 0.8), rough=1.0)


def mat_steam(name):
    """Principled Volume: drifting noise x spherical falloff x object property `steam` (keyed per object)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.remove(n["Principled BSDF"])
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.2, 2.2, 1.2)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    drv = mp.inputs["Location"].driver_add("default_value", 2).driver
    drv.type = "SCRIPTED"
    drv.expression = "-frame * 0.025"                 # steam rises through the noise field
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 6.0
    nz.inputs["Roughness"].default_value = 0.6
    l.new(mp.outputs[0], nz.inputs["Vector"])
    cr = n.new("ShaderNodeMapRange")
    cr.inputs["From Min"].default_value = 0.45
    cr.inputs["From Max"].default_value = 0.75
    l.new(nz.outputs["Fac"], cr.inputs["Value"])
    gr = n.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    col = n.new("ShaderNodeVectorMath")
    col.operation = "MULTIPLY"
    col.inputs[1].default_value = (1.0, 1.0, 0.55)  # tall column rather than a ball
    l.new(tc.outputs["Object"], col.inputs[0])
    l.new(col.outputs[0], gr.inputs["Vector"])
    at = n.new("ShaderNodeAttribute")
    at.attribute_type = "OBJECT"
    at.attribute_name = "steam"
    m1 = n.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    l.new(cr.outputs[0], m1.inputs[0])
    l.new(gr.outputs["Fac"], m1.inputs[1])
    m2 = n.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    l.new(m1.outputs[0], m2.inputs[0])
    l.new(at.outputs["Fac"], m2.inputs[1])
    pv = n.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.92, 0.92, 0.92, 1)
    l.new(m2.outputs[0], pv.inputs["Density"])
    l.new(pv.outputs[0], n["Material Output"].inputs["Volume"])
    return m


# ---------------------------------------------------------------------------------------------- architecture
def build_env():
    c = "ENV_BC_01"
    X0, X1, Y0, Y1, H, T = -4.0, 4.0, 0.0, 5.5, 2.8, 0.15
    tag(B.box("ENV_Floor", X0, X1, Y0, Y1, -0.05, 0.0, M["floor"], c), "light oak flooring, wide boards")
    tag(B.box("ENV_Ceiling", X0, X1, Y0, Y1, H, H + 0.05, M["arch"], c), "matte ivory plaster")
    tag(B.box("ENV_Wall_Back", X0 - T, X1 + T, Y1, Y1 + T, 0, H, M["arch"], c), "matte ivory plaster")
    tag(B.box("ENV_Wall_Front", X0 - T, X1 + T, Y0 - T, Y0, 0, H, M["arch"], c), "matte ivory plaster")
    tag(B.box("ENV_Wall_East", X1, X1 + T, Y0, Y1, 0, H, M["arch"], c), "matte ivory plaster")
    wy0, wy1, wz0, wz1 = 0.8, 4.8, 0.30, 2.55          # west window opening
    for nm, b in (("S", (Y0, wy0, 0, H)), ("N", (wy1, Y1, 0, H)), ("Sill", (wy0, wy1, 0, wz0)),
                  ("Head", (wy0, wy1, wz1, H))):
        tag(B.box("ENV_Wall_West_" + nm, X0 - T, X0, b[0], b[1], b[2], b[3], M["arch"], c), "matte ivory plaster")
    tag(B.box("ENV_Window_Glass", X0 - 0.08, X0 - 0.07, wy0, wy1, wz0, wz1, M["glass"], c), "low-iron glazing")
    for i, y in enumerate((wy0, wy0 + (wy1 - wy0) / 3, wy0 + 2 * (wy1 - wy0) / 3, wy1)):
        tag(B.box("ENV_Window_Mullion_%d" % i, X0 - 0.10, X0 - 0.04, y - 0.025, y + 0.025, wz0, wz1, M["metal"], c),
            "brushed bronze aluminium frame")
    for nm, z in (("Sill", wz0), ("Head", wz1)):
        tag(B.box("ENV_Window_Frame_" + nm, X0 - 0.10, X0 - 0.04, wy0, wy1, z - 0.025, z + 0.025, M["metal"], c),
            "brushed bronze aluminium frame")
    ext = B.box("ENV_Exterior_Backdrop", -40.0, -39.9, -30, 35, -10, 25, M["sky"], c)
    ext.visible_shadow = False
    tag(ext, "exterior plate: Singapore residential greenery / blocks (to be shot or sourced)")
    # kitchen: back run, tall unit, uppers, island with flush induction hob
    k = "ENV_BC_01"
    tag(B.box("KIT_Back_Plinth", 0.25, 3.15, 4.95, 5.45, 0.0, 0.10, M["joinery"], k), "warm natural oak")
    tag(B.box("KIT_Back_Base", 0.20, 3.20, 4.90, 5.50, 0.10, 0.87, M["joinery"], k, bev=0.002), "warm natural oak")
    tag(B.box("KIT_Back_Top", 0.20, 3.20, 4.88, 5.50, 0.87, 0.90, M["stone"], k, bev=0.002),
        "honed cream limestone 30 mm")
    tag(B.box("KIT_Backsplash", 0.20, 3.20, 5.48, 5.50, 0.90, 1.55, M["stone"], k), "honed cream limestone")
    tag(B.box("KIT_Uppers", 0.20, 3.20, 5.15, 5.48, 1.55, 2.30, M["joinery"], k, bev=0.002), "warm natural oak")
    tag(B.box("KIT_Tall_Unit", 3.20, 3.88, 4.90, 5.50, 0.0, 2.40, M["joinery"], k, bev=0.002), "warm natural oak")
    for i in range(1, 6):
        x = 0.20 + i * 0.5
        tag(B.box("KIT_Door_Gap_%d" % i, x - 0.0015, x + 0.0015, 4.895, 4.90, 0.12, 0.85, M["hob"], k), "shadow gap")
    tag(B.box("KIT_Sink", 1.40, 2.05, 5.00, 5.38, 0.899, 0.902, M["metal"], k), "brushed stainless undermount sink")
    tap = B.cyl("KIT_Tap", 0.014, 0.90, 1.22, M["metal"], k, loc=(1.72, 5.40))
    tag(tap, "brushed nickel tap")
    tag(B.box("KIT_Tap_Spout", 1.705, 1.735, 5.20, 5.41, 1.19, 1.215, M["metal"], k), "brushed nickel tap")
    tag(B.box("KIT_Island_Base", 0.70, 2.90, 3.00, 3.75, 0.0, 0.87, M["joinery"], k, bev=0.003), "warm natural oak")
    tag(B.box("KIT_Island_Top", 0.65, 2.95, 2.92, 3.80, 0.87, ISLAND_TOP, M["stone"], k, bev=0.003),
        "honed cream limestone 40 mm, softened arris")
    tag(B.box("KIT_Hob", 1.65, 2.25, 3.05, 3.60, ISLAND_TOP, HOB_TOP, M["hob"], k, bev=0.001),
        "black glass induction hob, flush")
    for i, x in enumerate((1.05, 2.55)):
        tag(B.cyl("KIT_Stool_Seat_%d" % i, 0.19, 0.62, 0.66, M["joinery"], k, loc=(x, 4.20), bev=0.005), "oak")
        tag(B.cyl("KIT_Stool_Post_%d" % i, 0.025, 0.0, 0.62, M["metal"], k, loc=(x, 4.20)), "brushed steel")
    for i, x in enumerate((1.30, 2.60)):
        tag(B.cyl("KIT_Pendant_%d" % i, 0.11, 1.80, 1.96, M["ceramic"], k, loc=(x, 3.36)), "handmade ceramic shade")
        tag(B.cyl("KIT_Pendant_Cord_%d" % i, 0.003, 1.96, 2.8, M["hob"], k, loc=(x, 3.36)), "black cord")
    tag(B.box("KIT_Board", 2.40, 2.82, 3.25, 3.55, ISLAND_TOP, ISLAND_TOP + 0.025, M["joinery"], k, bev=0.004),
        "end-grain oak board")
    tag(B.cyl("KIT_Crock", 0.06, 0.90, 1.06, M["ceramic"], k, loc=(0.55, 5.20)), "handmade ceramic crock")
    tag(B.cyl("KIT_Oil", 0.03, 0.90, 1.17, M["glass"], k, loc=(0.75, 5.25)), "glass oil bottle")
    # dining
    tag(B.box("DIN_Table_Top", -3.05, -1.65, 2.15, 3.05, TABLE_TOP - 0.035, TABLE_TOP, M["joinery"], k, bev=0.004),
        "warm natural oak, oiled")
    for i, (x, y) in enumerate(((-2.98, 2.22), (-1.72, 2.22), (-2.98, 2.98), (-1.72, 2.98))):
        tag(B.box("DIN_Table_Leg_%d" % i, x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0, TABLE_TOP - 0.035, M["joinery"],
                  k), "oak")
    for i, (x, y, rot) in enumerate(((-3.45, 2.60, 0), (-2.35, 3.45, 90), (-1.25, 2.60, 180))):
        ch = chair("DIN_Chair_%d" % i, k)
        ch.location = (x, y, 0)
        ch.rotation_euler.z = math.radians(rot)
    tag(B.box("DIN_Runner", -3.00, -1.70, 2.45, 2.88, TABLE_TOP, TABLE_TOP + 0.002, M["linen"], k),
        "natural linen runner")
    tag(B.cyl("DIN_Pendant", 0.22, 1.55, 1.70, M["ceramic"], k, loc=(-2.35, 2.60)), "handmade ceramic pendant")
    tag(B.cyl("DIN_Pendant_Cord", 0.003, 1.70, 2.8, M["hob"], k, loc=(-2.35, 2.60)), "black cord")
    tag(B.cyl("DIN_Glass", 0.035, TABLE_TOP, TABLE_TOP + 0.11, M["glass"], k, loc=(-2.62, 2.50)), "tumbler")
    tag(B.cyl("DIN_Jug", 0.05, TABLE_TOP, TABLE_TOP + 0.18, M["ceramic"], k, loc=(-2.80, 2.80)),
        "handmade ceramic water jug")
    tag(B.cyl("DIN_Plant_Pot", 0.18, 0.0, 0.42, M["ceramic"], k, loc=(-3.60, 4.95)), "ceramic planter")
    tag(B.sphere("DIN_Plant", 0.38, (-3.60, 4.95, 0.95), M["linen"], k, scale=(1, 1, 1.4)), "fiddle-leaf fig")


def chair(name, c):
    bm = bmesh.new()
    B.bm_box(bm, -0.22, 0.22, -0.22, 0.22, 0.43, 0.47)
    B.bm_box(bm, -0.24, -0.20, -0.22, 0.22, 0.47, 0.85)
    for x, y in ((-0.19, -0.19), (0.19, -0.19), (-0.19, 0.19), (0.19, 0.19)):
        B.bm_box(bm, x - 0.018, x + 0.018, y - 0.018, y + 0.018, 0.0, 0.43)
    ob = B.mesh_obj(name, bm, c, M["joinery"])
    return tag(ob, "oak dining chair, linen seat pad")


# ---------------------------------------------------------------------------------------------- product carton
def carton(name, c, data=None):
    """Upright carton, origin at bottom centre, front (artwork face) toward -Y. UVs form a dieline cross:
    [left D][front W][right D][back W] across, top/bottom flaps above/below the front panel."""
    w, d, h = CARTON["w"], CARTON["d"], CARTON["h"]
    if data is None:
        bm = bmesh.new()
        x0, x1, y0, y1 = -w / 2, w / 2, -d / 2, d / 2
        v = {k: bm.verts.new(p) for k, p in dict(
            a=(x0, y0, 0), b=(x1, y0, 0), c=(x1, y1, 0), d=(x0, y1, 0),
            e=(x0, y0, h), f=(x1, y0, h), g=(x1, y1, h), h=(x0, y1, h)).items()}
        U = 2 * w + 2 * d
        s = 1.0 / U
        vo = (1.0 - (h + 2 * d) * s) / 2               # centre the cross vertically in UV space
        faces = {  # face: (verts ccw from outside, uv rect u0,v0,u1,v1 in metres on the dieline)
            "front": ("abfe", (d, d, d + w, d + h)),
            "right": ("bcgf", (d + w, d, 2 * d + w, d + h)),
            "back": ("cdhg", (2 * d + w, d, U, d + h)),
            "left": ("daeh", (0, d, d, d + h)),
            "top": ("efgh", (d, d + h, d + w, 2 * d + h)),
            "bottom": ("dcba", (d, 0, d + w, d)),
        }
        uvl = bm.loops.layers.uv.new("DIELINE")
        for nm, (vs, (u0, v0, u1, v1)) in faces.items():
            f = bm.faces.new([v[k] for k in vs])
            corners = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
            if nm == "bottom":
                corners = [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]
            for lp, (u, vv) in zip(f.loops, corners):
                lp[uvl].uv = (u * s, vv * s + vo)
        ob = B.mesh_obj(name, bm, c, M["carton"])
        sd = ob.modifiers.new("Board_0.6mm", "SOLIDIFY")
        sd.thickness = 0.0006
        sd.offset = -1.0
        B.bevel(ob, 0.0012, 3)
    else:
        ob = bpy.data.objects.new(name, data)
        B.link(ob, c)
    ob.pass_index = 1
    ob["dimensions_mm"] = json.dumps({"width": w * 1000, "depth": d * 1000, "height": h * 1000,
                                      "status": "PROVISIONAL (spec value); replace with measured carton"})
    return tag(ob, "paperboard, official Bowl Curry Spicy Madras 300g artwork via DIELINE UVs (not supplied yet)")


# ---------------------------------------------------------------------------------------------- cookware & food
def build_pan():
    c = "PROP_PAN_01"
    prof = [(0.0, 0.0), (0.122, 0.0), (0.131, 0.004), (0.1450, 0.050), (0.1450, 0.053), (0.1400, 0.053),
            (0.1230, 0.0080), (0.1180, 0.0065), (0.0, 0.0065)]
    pan = B.lathe("PAN_Body", prof, M["iron"], c, loc=PAN_C, n=96)
    tag(pan, "seasoned cast iron, 280 mm top inner diameter, 5 mm wall, 6.5 mm base")
    bm = bmesh.new()
    B.bm_box(bm, 0.140, 0.315, -0.016, 0.016, 0.034, 0.048)
    B.bm_box(bm, -0.180, -0.140, -0.022, 0.022, 0.040, 0.050)
    h = B.mesh_obj("PAN_Handle_And_Lip", bm, c, M["iron"])
    h.location = PAN_C
    h.rotation_euler.z = math.radians(-35)             # handle toward camera-right / front
    B.bevel(h, 0.004, 2)
    tag(h, "cast iron, integral handle and helper lip")
    pan.rotation_euler.z = h.rotation_euler.z


def blob(name, c, mat, dims, seed, flat=0.75):
    """Irregular piece: icosphere with deterministic noise displacement and a flattened seared base."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    off = Vector((seed * 3.17, seed * 1.31, seed * 2.03))
    for v in bm.verts:
        p = v.co.copy()
        k = 1.0 + 0.22 * noise.noise(p * 1.7 + off) + 0.07 * noise.noise(p * 5.0 + off)
        p *= k
        p = Vector((p.x * dims[0] / 2, p.y * dims[1] / 2, p.z * dims[2] / 2))
        p.z = max(p.z, -flat * dims[2] / 2)
        v.co = p
    ob = B.mesh_obj(name, bm, c, mat, smooth=True)
    return ob


def build_food():
    rnd = random.Random(7)
    c = "FOOD_CHICKEN_01"
    offs = [(0.0, 0.0), (0.072, 0.020), (-0.062, 0.050), (0.020, -0.078), (-0.076, -0.034), (0.058, -0.060),
            (-0.020, 0.086), (0.080, 0.070), (-0.045, -0.085)]
    for i, (dx, dy) in enumerate(offs):
        dims = (rnd.uniform(0.045, 0.060), rnd.uniform(0.034, 0.044), rnd.uniform(0.024, 0.032))
        ob = blob("CHICKEN_%02d" % i, c, M["food"], dims, i + 1)
        ob.location = (PAN_C.x + dx, PAN_C.y + dy, PAN_FLOOR + 0.75 * dims[2] / 2)
        ob.rotation_euler.z = rnd.uniform(0, math.pi)
        tag(ob, "fully cooked chicken thigh piece, golden sear, rough torn edges")
    # sauce level proxy in the pan (rises while the pour settles between the pieces)
    hs = 0.012                                         # final sauce depth: pieces stay proud of the surface
    rt = 0.1205 + (0.0065 + hs) * (0.017 / 0.045)
    s = B.lathe("SAUCE_PAN_LEVEL", [(0.0, 0.0), (0.1185, 0.0), (rt, hs), (0.0, hs)], M["sauce"], "FOOD_SAUCE_01",
                loc=(PAN_C.x, PAN_C.y, PAN_FLOOR + 0.0003), n=96, smooth=False)
    tag(s, "opaque rich brown Madras curry, fine spice particles, slight oil separation (Mantaflow mesh later)")
    for f, sz, hid in ((1, 0.02, True), (129, 0.02, True), (130, 0.02, False), (150, 0.55, False),
                       (200, 1.0, False)):
        s.scale.z = sz
        s.hide_render = hid
        s.keyframe_insert("scale", index=2, frame=f)
        s.keyframe_insert("hide_render", frame=f)
    const(s, "hide_render")
    # pour vessel proxy + stream
    pc = "FOOD_SAUCE_01"
    pouch = B.box("PROP_POUCH_PROXY", -0.065, 0.065, -0.010, 0.010, -0.09, 0.09, M["food"], pc, bev=0.004)
    tag(pouch, "PROVISIONAL pour vessel (inner pack format to be confirmed by client)")
    for f, loc, ry in ((121, (1.42, 3.30, 1.30), 0), (128, (1.74, 3.30, 1.10), 110), (158, (1.74, 3.30, 1.10), 112),
                       (168, (1.42, 3.30, 1.32), 20)):
        pouch.location = loc
        pouch.rotation_euler.y = math.radians(ry)
        pouch.keyframe_insert("location", frame=f)
        pouch.keyframe_insert("rotation_euler", frame=f)
    for f, hid in ((1, True), (120, True), (121, False), (168, False), (169, True)):
        pouch.hide_render = hid
        pouch.keyframe_insert("hide_render", frame=f)
    const(pouch, "hide_render")
    top = Vector((1.826, 3.30, 1.069))
    bot_z = PAN_FLOOR + 0.004
    L = top.z - bot_z
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.0045, radius2=0.0065, depth=1.0,
                          matrix=Matrix.Translation((0, 0, -0.5)))
    st = B.mesh_obj("SAUCE_STREAM_PROXY", bm, pc, M["sauce"], smooth=True)
    tag(st, "gravity-driven sauce stream (Mantaflow liquid mesh at detail stage)")
    st.location = top
    # stream grows down 128-132, holds, then the tail detaches and falls 156-162
    keys = [(127, top.z, 0.001, True), (128, top.z, 0.001, False), (132, top.z, L, False), (156, top.z, L, False),
            (162, bot_z + 0.02, 0.02, False), (163, bot_z, 0.001, True)]
    for f, z, sz, hid in keys:
        st.location.z = z
        st.scale = (1, 1, sz)
        st.hide_render = hid
        st.keyframe_insert("location", index=2, frame=f)
        st.keyframe_insert("scale", index=2, frame=f)
        st.keyframe_insert("hide_render", frame=f)
    st.hide_render = True
    st.keyframe_insert("hide_render", frame=1)
    const(st, "hide_render")
    # spice spoon + particles (ballistic keyed proxies; particle system at detail stage)
    sc_ = "FOOD_SPICE_01"
    spoon = B.lathe("PROP_SPICE_SPOON", [(0.0, 0.0), (0.020, 0.004), (0.026, 0.014), (0.024, 0.014),
                                         (0.018, 0.006), (0.0, 0.003)], M["metal"], sc_, n=32)
    hb = bmesh.new()
    B.bm_box(hb, 0.024, 0.17, -0.005, 0.005, 0.011, 0.016)
    hdl = B.mesh_obj("PROP_SPICE_SPOON_Handle", hb, sc_, M["metal"])
    hdl.parent = spoon
    tag(spoon, "brushed steel measuring spoon")
    tag(hdl, "brushed steel")
    tip = Vector((2.00, 3.38, 1.03))
    for f, loc, rx in ((168, (2.10, 3.62, 1.20), 0), (176, tuple(tip), 0), (184, tuple(tip), -70),
                       (196, (2.12, 3.64, 1.22), -20)):
        spoon.location = loc
        spoon.rotation_euler = (math.radians(rx), 0, math.radians(-120))
        spoon.keyframe_insert("location", frame=f)
        spoon.keyframe_insert("rotation_euler", frame=f)
    for f, hid in ((1, True), (167, True), (168, False), (196, False), (197, True)):
        spoon.hide_render = hid
        spoon.keyframe_insert("hide_render", frame=f)
        hdl.hide_render = hid
        hdl.keyframe_insert("hide_render", frame=f)
    const(spoon, "hide_render")
    const(hdl, "hide_render")
    pm = bmesh.new()
    bmesh.ops.create_icosphere(pm, subdivisions=1, radius=1.0)
    pme = bpy.data.meshes.new("SPICE_GRAIN")
    pm.to_mesh(pme)
    pm.free()
    pme.materials.append(M["spice"])
    land = PAN_FLOOR + 0.0003 + 0.012 * 0.95
    g = 9.81
    for i in range(70):
        ob = bpy.data.objects.new("SPICE_%02d" % i, pme)
        B.link(ob, sc_)
        tag(ob, "signature spice mix grain/flake (particle system at detail stage)")
        r = rnd.uniform(0.0016, 0.0032)
        ob.scale = (r, r, r * 0.7)
        f0 = 178 + rnd.randint(0, 6)
        p0 = tip + Vector((rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), -0.008))
        v0 = Vector((rnd.uniform(-0.12, 0.12), rnd.uniform(-0.10, 0.06), rnd.uniform(-0.05, 0.02)))
        ob.hide_render = True
        ob.location = p0
        for kf in (1, f0 - 1):
            ob.keyframe_insert("hide_render", frame=kf)
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=f0)
        const(ob, "hide_render")
        t = 0.0
        f = f0
        while True:
            p = p0 + v0 * t + Vector((0, 0, -0.5 * g * t * t))
            done = p.z <= land
            if done:
                p.z = land
            ob.location = p
            ob.keyframe_insert("location", frame=f)
            if done:
                break
            f += 1
            t = (f - f0) / FPS
        for fc in B.fcurves_of(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR" if fc.data_path == "location" else "CONSTANT"
    # serving bowl, curry, rice
    bc = "PROP_BOWL_01"
    bowl = B.lathe("BOWL_Serving", [(0.0, 0.0), (0.040, 0.0), (0.042, 0.010), (0.090, 0.075), (0.085, 0.076),
                                    (0.040, 0.016), (0.0, 0.016)], M["ceramic"], bc, loc=BOWL_C, n=96)
    tag(bowl, "handmade ceramic bowl, 180 mm, reactive glaze, irregular rim")
    cur = B.lathe("CURRY_IN_BOWL", [(0.0, 0.016), (0.042, 0.016), (0.0726, 0.058), (0.0, 0.058)], M["sauce"],
                  "FOOD_SAUCE_01", loc=BOWL_C, n=96)
    tag(cur, "finished Chicken Madras surface, restrained highlights")
    for i, (dx, dy) in enumerate(((-0.02, 0.01), (0.025, -0.015), (0.005, 0.03), (0.03, 0.025))):
        dims = (rnd.uniform(0.038, 0.048), rnd.uniform(0.030, 0.036), rnd.uniform(0.022, 0.028))
        ob = blob("CHICKEN_BOWL_%02d" % i, "FOOD_CHICKEN_01", M["food"], dims, 20 + i)
        ob.location = BOWL_C + Vector((dx, dy, 0.058 + 0.002))
        ob.rotation_euler.z = rnd.uniform(0, math.pi)
        tag(ob, "chicken piece emerging from sauce")
    rb = B.lathe("BOWL_Rice", [(0.0, 0.0), (0.032, 0.0), (0.034, 0.008), (0.065, 0.055), (0.061, 0.056),
                               (0.032, 0.012), (0.0, 0.012)], M["ceramic"], bc, loc=RICE_C, n=96)
    tag(rb, "handmade ceramic rice bowl")
    rice = B.sphere("RICE_Mound", 0.058, RICE_C + Vector((0, 0, 0.040)), M["linen"], "FOOD_RICE_01",
                    scale=(1, 1, 0.45))
    rice.data.materials[0] = M["ceramic"]
    tag(rice, "steamed basmati, individual grains at detail stage")
    mat_ = B.box("DIN_Placemat", BOWL_C.x - 0.20, BOWL_C.x + 0.20, BOWL_C.y - 0.15, BOWL_C.y + 0.15, TABLE_TOP + 0.0022,
                 TABLE_TOP + 0.004, M["linen"], "ENV_BC_01")
    tag(mat_, "natural linen placemat")


def const(ob, path):
    for fc in B.fcurves_of(ob):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


# ---------------------------------------------------------------------------------------------- steam
def steam(name, centre, size, keys):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    ob = B.mesh_obj(name, bm, "FX_STEAM", M["steam"])
    ob.location = centre + Vector((0, 0, size[2]))
    ob.scale = size
    ob.visible_shadow = False
    ob["steam"] = 0.0
    for f, v in keys:
        ob["steam"] = v
        ob.keyframe_insert('["steam"]', frame=f)
    return tag(ob, "restrained steam (Mantaflow smoke / volume at detail stage)")


# ---------------------------------------------------------------------------------------------- cameras & lights
def cam_rig(cid, keys, fstop):
    """keys: [(frame, pos, target, lens)] - Bezier (auto-clamped) location/target/lens keys."""
    c = "CAMERAS"
    cd = bpy.data.cameras.new(cid)
    cd.sensor_width = 36.0
    cd.clip_start = 0.01
    cd.clip_end = 200.0
    cam = bpy.data.objects.new(cid, cd)
    B.link(cam, c)
    tgt = B.empty(cid + "_TARGET", keys[0][2], c, "SPHERE", 0.03)
    tc = cam.constraints.new("TRACK_TO")
    tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    cd.dof.use_dof = True
    cd.dof.focus_object = tgt
    cd.dof.aperture_fstop = fstop
    for f, pos, t, lens in keys:
        cam.location = pos
        tgt.location = t
        cd.lens = lens
        cam.keyframe_insert("location", frame=f)
        tgt.keyframe_insert("location", frame=f)
        cd.keyframe_insert("lens", frame=f)
    return cam


CAM_A_KEYS = [  # frame, position, target, lens(mm)            beat
    (1, (0.90, 0.55, 1.60), (0.20, 4.20, 1.05), 24),  # kitchen establishment
    (40, (1.25, 1.10, 1.45), (1.00, 3.60, 1.00), 28),
    (66, (1.27, 2.30, 1.06), (1.30, 3.26, 1.00), 50),  # packaging reveal
    (84, (1.50, 2.38, 1.12), (1.62, 3.30, 0.98), 50),
    (102, (1.95, 2.62, 1.32), (1.95, 3.32, 0.94), 50),  # cooked chicken
    (120, (1.98, 2.64, 1.30), (1.95, 3.32, 0.94), 50),
    (140, (2.30, 2.72, 1.12), (1.92, 3.30, 0.99), 65),  # sauce pour
    (165, (2.26, 2.76, 1.10), (1.92, 3.30, 0.98), 65),
    (190, (1.70, 2.86, 1.14), (1.98, 3.34, 0.97), 65),  # spice addition
    (208, (1.92, 2.96, 1.12), (1.95, 3.32, 0.94), 85),  # simmering macro
    (240, (1.94, 3.10, 1.07), (1.95, 3.34, 0.95), 100),  # into the steam
]
CAM_B_KEYS = [
    (241, (-2.30, 2.47, 1.04), (-2.30, 2.60, 0.80), 50),  # out of the steam column: serving bowl
    (288, (-2.08, 1.86, 0.99), (-2.17, 2.68, 0.84), 45),  # dining + hero composition
    (360, (-2.08, 1.86, 0.99), (-2.17, 2.68, 0.84), 45),  # 3 s hold (288-360)
]
BEATS = [(1, "Kitchen establishment"), (49, "Packaging reveal"), (91, "Cooked chicken"), (121, "Sauce pour"),
         (169, "Spice addition"), (197, "Simmering macro"), (236, "Steam transition"), (241, "Serving bowl reveal"),
         (263, "Dining environment"), (288, "Hero hold")]


def build_cameras(sc):
    a = cam_rig("CAM_A", CAM_A_KEYS, 5.6)
    b = cam_rig("CAM_B", CAM_B_KEYS, 4.0)
    sc.camera = a
    for f, cam in ((1, a), (CUT, b)):
        m = sc.timeline_markers.new(cam.name, frame=f)
        m.camera = cam
    for f, nm in BEATS:
        sc.timeline_markers.new("BEAT_%03d %s" % (f, nm), frame=f)
    return a, b


def build_lights():
    c = "LIGHTS"
    win = B.light("LGT_WINDOW_SOFT", "AREA", (-3.93, 2.80, 1.42), 650.0, c, k=5600, size=2.25, size_y=4.0,
                  rot=(0, math.radians(-90), 0))
    ld = win.data
    for f, k, e in ((1, 5600, 650.0), (240, 5600, 650.0), (241, 4300, 520.0), (360, 4300, 520.0)):
        ld.color = B.kelvin_rgb(k)
        ld.energy = e
        ld.keyframe_insert("color", frame=f)
        ld.keyframe_insert("energy", frame=f)
    sun = B.light("LGT_SUN_LATE_AFTERNOON", "SUN", (-6, 2.6, 3), 0.0, c, k=3600)
    d = Vector((1.0, 0.15, -0.36)).normalized()     # low western sun through the window onto the table
    sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sun.data.angle = math.radians(1.5)
    for f, e in ((1, 0.0), (240, 0.0), (241, 1.6), (360, 1.6)):
        sun.data.energy = e
        sun.data.keyframe_insert("energy", frame=f)
    fill = B.light("LGT_CEILING_BOUNCE", "AREA", (0.0, 2.75, 2.75), 40.0, c, k=4800, size=3.0, size_y=2.0)
    fill.visible_camera = False
    for ob in (win, sun):
        for fc in B.fcurves_of(ob.data):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    w = bpy.data.worlds.new("WORLD_DAYLIGHT_NEUTRAL")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.78, 0.82, 0.88, 1)
    bg.inputs["Strength"].default_value = 0.55
    bpy.context.scene.world = w


# ---------------------------------------------------------------------------------------------- liquid sim setup
def build_mantaflow_setup():
    """Domain/inflow/effectors for the pour. Not baked. Values marked PROVISIONAL pending viscosity calibration."""
    c = "SIM_MANTAFLOW"
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    dom = B.mesh_obj("SIM_SAUCE_DOMAIN", bm, c)
    dom.location = (PAN_C.x - 0.04, PAN_C.y, HOB_TOP + 0.09)
    dom.scale = (0.40, 0.34, 0.20)
    md = dom.modifiers.new("Fluid", "FLUID")
    md.fluid_type = "DOMAIN"
    ds = md.domain_settings
    ds.domain_type = "LIQUID"
    ds.resolution_max = 128
    ds.use_viscosity = True
    ds.viscosity_base = 2.0                             # PROVISIONAL: 2.0e-3 m^2/s kinematic (see README)
    ds.viscosity_exponent = 3
    ds.use_mesh = True
    ds.cache_directory = "//cache_sauce"
    ds.cache_frame_start, ds.cache_frame_end = 121, 240
    inf = B.cyl("SIM_SAUCE_INFLOW", 0.006, -0.006, 0.006, None, c, loc=(1.826, 3.30))
    inf.location.z = 1.06
    mf = inf.modifiers.new("Fluid", "FLUID")
    mf.fluid_type = "FLOW"
    fs = mf.flow_settings
    fs.flow_type = "LIQUID"
    fs.flow_behavior = "INFLOW"
    fs.use_initial_velocity = True
    fs.velocity_coord = (0.0, 0.0, -0.25)
    for f, on in ((121, False), (128, True), (156, True), (157, False)):
        fs.use_inflow = on
        fs.keyframe_insert("use_inflow", frame=f)
    for ob in [bpy.data.objects["PAN_Body"]] + [o for o in bpy.data.objects if o.name.startswith("CHICKEN_0")]:
        e = ob.modifiers.new("Fluid", "FLUID")
        e.fluid_type = "EFFECTOR"
        e.effector_settings.effector_type = "COLLISION"
    for o in (dom, inf):
        o.hide_render = True
        o.display_type = "WIRE"
    dom["status"] = "NOT BAKED - awaiting viscosity calibration of the prepared product"


# ---------------------------------------------------------------------------------------------- render settings
def render_settings(sc):
    r = sc.render
    sc.frame_start, sc.frame_end = 1, F_END
    r.fps = FPS
    r.resolution_x, r.resolution_y = 3840, 2160
    r.engine = "CYCLES"
    sc.cycles.device = "GPU"                            # falls back to CPU when no GPU device is configured
    sc.cycles.samples = 256
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.volume_bounces = 2
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5                         # 180-degree shutter
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = -0.3
    sc.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in [
        i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items] else "None"
    s = r.image_settings
    if hasattr(s, "media_type"):
        s.media_type = "MULTI_LAYER_IMAGE"
    s.file_format = "OPEN_EXR_MULTILAYER"
    s.exr_codec = "DWAA"
    s.color_depth = "16"
    r.filepath = "//../renders/final/BC_MADRAS_####"
    vl = sc.view_layers[0]
    vl.name = "BEAUTY"
    vl.use_pass_z = True
    vl.use_pass_object_index = True
    vl.use_pass_cryptomatte_object = True
    vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = vl.use_pass_diffuse_color = True
    vl.use_pass_glossy_direct = vl.use_pass_glossy_indirect = vl.use_pass_glossy_color = True
    vl.cycles.use_pass_volume_direct = vl.cycles.use_pass_volume_indirect = True
    vl.cycles.use_pass_shadow_catcher = True
    vl.use_pass_vector = True


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "BC_MADRAS_MASTER"
    for cn in ("ENV_BC_01", "BC_MADRAS_01", "PROP_PAN_01", "FOOD_CHICKEN_01", "FOOD_SAUCE_01", "FOOD_SPICE_01",
               "PROP_BOWL_01", "FOOD_RICE_01", "FX_STEAM", "CAMERAS", "LIGHTS", "SIM_MANTAFLOW"):
        B.coll(cn)
    build_materials()
    build_env()
    k = carton("BC_MADRAS_01_ISLAND", "BC_MADRAS_01")
    k.location = ISLAND_CARTON
    k.rotation_euler.z = math.radians(8)
    h = carton("BC_MADRAS_01_HERO", "BC_MADRAS_01", data=k.data)
    for md in k.modifiers:
        n = h.modifiers.new(md.name, md.type)
        for p in ("thickness", "offset", "width", "segments", "limit_method"):
            if hasattr(md, p):
                setattr(n, p, getattr(md, p))
    h.location = HERO_CARTON
    h.rotation_euler.z = math.radians(-6)
    build_pan()
    build_food()
    steam("STEAM_PAN", PAN_C + Vector((0, 0, 0.02)), (0.17, 0.17, 0.30),
          [(1, 0.0), (130, 0.0), (145, 0.6), (200, 0.8), (226, 0.9), (234, 2.0), (237, 8.0), (240, 40.0), (241, 40.0), (252, 0.8), (360, 0.8)])
    steam("STEAM_BOWL", BOWL_C + Vector((0, 0, 0.06)), (0.18, 0.18, 0.30),
          [(1, 0.0), (240, 0.0), (241, 40.0), (245, 14.0), (252, 3.0), (262, 1.0), (288, 0.6), (360, 0.6)])
    build_lights()
    build_cameras(sc)
    build_mantaflow_setup()
    lc = sc.view_layers[0].layer_collection.children["SIM_MANTAFLOW"]
    lc.exclude = True
    render_settings(sc)
    sc.frame_set(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    print("BUILD_DONE", OUT)


main()
