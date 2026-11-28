"""Builds POLYCAB_GLISS_MASTER.blend for "In the Best Light" (15 s, 10 shots, 360 frames @ 24 fps).

    blender -b --factory-startup --python scripts/build_gliss.py

Scenes
  SCENE_PRODUCT_STUDIO       shots 1, 2, 10 (studio), product instance, studio light rig
  SCENE_ARCHITECTURE         shots 3-9, room 7 x 6 x 3.1 m, two installed Gliss fixtures, cast proxies
  SCENE_WALKTHROUGH_PREVIEW  10 s technical walkthrough, same room collections, no cast, fixtures on
  SCENE_MASTER_EDIT          VSE: one scene strip per shot, 360 frames, timeline markers
All scenes share master frame numbering (shot N renders master frames of shot N from its own scene).

Units: metres in Blender, millimetres in the dimension register (scripts/gliss_product.py).
Accent-light state: the scene custom property `gliss_on` (0/1, constant keys) drives every Gliss spot light and the
visible COB emission through Context-Property drivers, so one shared material serves all scenes."""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "polycab_superior_switch", "scripts"))
import gliss_product as GP  # noqa: E402
import build_scene as B     # noqa: E402  (material and mesh helpers only)

OUT_BLEND = os.path.join(ROOT, "scenes", "POLYCAB_GLISS_MASTER.blend")
ART_IMAGE = os.path.join(ROOT, "reference", "ART_WEDDING_01_ANIMATIC_PLACEHOLDER.png")
FPS = 24
CEIL = 3.1
RX0, RX1, RY0, RY1 = -3.5, 3.5, 0.0, 6.0
FIXTURES = [((-0.725, 0.95, CEIL), (-0.45, 0.04, 1.65)), ((0.725, 0.95, CEIL), (0.45, 0.04, 1.65))]
ISHA = (0.30, 2.0)          # swapped from the brief's proposed (-0.3) so Isha is screen-left from cameras at +Y
VEER = (-0.30, 2.0)
SHOTS = [  # id, scene, first, last
    ("CAM_01_PRODUCT_HERO", "SCENE_PRODUCT_STUDIO", 1, 36),
    ("CAM_02_COB_MACRO", "SCENE_PRODUCT_STUDIO", 37, 60),
    ("CAM_03_AMBIENT", "SCENE_ARCHITECTURE", 61, 84),
    ("CAM_04_TRANSFORMATION", "SCENE_ARCHITECTURE", 85, 108),
    ("CAM_05_WEDDING_MEMORY", "SCENE_ARCHITECTURE", 109, 132),
    ("CAM_06_MATCH_CUT", "SCENE_ARCHITECTURE", 133, 168),
    ("CAM_07_HUMAN_CONNECTION", "SCENE_ARCHITECTURE", 169, 204),
    ("CAM_08_INSTALLED_GLISS", "SCENE_ARCHITECTURE", 205, 228),
    ("CAM_09_ARCHITECTURAL_REVEAL", "SCENE_ARCHITECTURE", 229, 276),
    ("CAM_10_FINAL_PACKSHOT", "SCENE_PRODUCT_STUDIO", 277, 360),
]
MARKERS = [(1, "01_PRODUCT_HERO"), (37, "02_COB_MACRO"), (61, "03_AMBIENT"), (85, "04_TRANSFORMATION"),
           (109, "05_WEDDING_MEMORY"), (133, "06_MATCH_CUT"), (169, "07_HUMAN_CONNECTION"),
           (205, "08_INSTALLED_GLISS"), (229, "09_ARCHITECTURAL_REVEAL"), (277, "10_FINAL_PACKSHOT")]
LIGHT_ON_FRAME = 85
GLISS_PREVIEW = dict(beam_angle_deg=36.0, beam_blend=0.35, light_output_w=70.0, cct_k=3000)

# ---------------------------------------------------------------- collections / scenes
_TARGET = {"scene": None}


def scene(name):
    sc = bpy.data.scenes.get(name)
    if sc is None:
        sc = bpy.data.scenes.new(name)
    return sc


COLL_ALIAS = {"02_INTERIOR_ASSETS": "02_ARCHITECTURAL_ENVIRONMENT"}


def coll(name, parent=None):
    name = COLL_ALIAS.get(name, name)
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        if parent is not None:
            parent.children.link(c)
    if parent is None and _TARGET["scene"] is not None and \
            c.name not in _TARGET["scene"].collection.children:
        _TARGET["scene"].collection.children.link(c)
    return c


B.coll = coll   # route the borrowed helpers' collection lookups here


def exclude(vl, cname, value=True):
    if vl.layer_collection is None:
        vl.update()
    vl.layer_collection.children[cname].exclude = value


def link(ob, cname):
    coll(cname).objects.link(ob)
    return ob


def ease(idb, vector_first=False):
    ad = getattr(idb, "animation_data", None)
    for fc in B.fcurves_of(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        fc.update()


def constant(idb):
    for fc in B.fcurves_of(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def ctx_driver(idb, path, expr, index=-1, extra=None):
    """Driver reading the *rendering* scene's custom properties (Context Property: active scene)."""
    fc = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name = "on"
    v.type = "CONTEXT_PROP"
    v.targets[0].context_property = "ACTIVE_SCENE"
    v.targets[0].data_path = '["gliss_on"]'
    for name, (ob, prop) in (extra or {}).items():
        w = d.variables.new()
        w.name = name
        w.type = "SINGLE_PROP"
        w.targets[0].id = ob
        w.targets[0].data_path = '["%s"]' % prop
    d.expression = expr
    return fc


# ---------------------------------------------------------------- materials
M = {}


def build_materials():
    B.build_materials()           # also provides walnut / fabric / ceramic etc. from the shared library
    M.update(B.MAT)
    # product
    m, n, l, b = B._mat("MAT_BLACK_ALUMINIUM")
    B._set(b, base=(0.0103, 0.0103, 0.0103), metal=0.15, rough=0.38, spec=0.5)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2600.0
    nz.inputs["Detail"].default_value = 2.0
    mp = B._coords(n)
    l.new(mp.outputs[0], nz.inputs["Vector"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.35
    rr.inputs["To Max"].default_value = 0.41
    l.new(nz.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs["Result"], b.inputs["Roughness"])
    B._bump(n, l, nz.outputs["Fac"], b, 0.04, 0.00005)
    m["note"] = "#191919 sRGB, metallic 0.15, roughness 0.38 starting values; match to the official photograph"
    M["MAT_BLACK_ALUMINIUM"] = m
    M["MAT_BLACK_RECESS"] = B.mat_plain("MAT_BLACK_RECESS", (0.002, 0.002, 0.002), rough=0.8)
    M["MAT_REFLECTOR_ALUMINIUM"] = B.mat_plain("MAT_REFLECTOR_ALUMINIUM", (0.91, 0.91, 0.92), rough=0.16,
                                               metal=1.0)
    # COB: yellow phosphor when off; emission only to camera and glossy rays when on (the spot light does the
    # illumination, so the visible emitter never double-counts diffuse light)
    m, n, l, b = B._mat("MAT_COB_PHOSPHOR")
    B._set(b, base=(0.78, 0.62, 0.12), rough=0.55, spec=0.3, sss=0.1)
    em = n.new("ShaderNodeEmission")
    em.name = "COB_Emission"
    em.inputs["Color"].default_value = (*B.kelvin_rgb(GLISS_PREVIEW["cct_k"]), 1)
    em.inputs["Strength"].default_value = 0.0
    lp = n.new("ShaderNodeLightPath")
    mx = n.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    l.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    l.new(lp.outputs["Is Glossy Ray"], mx.inputs[1])
    gate = n.new("ShaderNodeMath")
    gate.operation = "MULTIPLY"
    l.new(mx.outputs[0], gate.inputs[0])
    gate.name = "COB_On"
    at = n.new("ShaderNodeAttribute")
    at.attribute_type = "INSTANCER"
    at.attribute_name = "cob_on"           # custom property on each head instance (keyed with its spot light)
    l.new(at.outputs["Fac"], gate.inputs[1])
    mixs = n.new("ShaderNodeMixShader")
    l.new(gate.outputs[0], mixs.inputs["Fac"])
    l.new(b.outputs[0], mixs.inputs[1])
    l.new(em.outputs[0], mixs.inputs[2])
    l.new(mixs.outputs[0], n["Material Output"].inputs["Surface"])
    em.inputs["Strength"].default_value = 60.0
    M["MAT_COB_PHOSPHOR"] = m
    # architecture
    M["Travertine"] = mat_travertine("MAT_TRAVERTINE_HONED")
    M["Oak"] = B.mat_wood("MAT_OAK_DARK", (0.06, 0.035, 0.02), (0.16, 0.095, 0.05), 0.42, axis="Y", stretch=0.1,
                          plank=(1.8, 0.18), coat=0.2)
    M["Walnut"] = B.mat_wood("MAT_WALNUT_DARK", (0.045, 0.022, 0.012), (0.17, 0.085, 0.045), 0.4, axis="X",
                             stretch=0.12, coat=0.25)
    M["WalnutV"] = B.mat_wood("MAT_WALNUT_DARK_VERTICAL", (0.045, 0.022, 0.012), (0.17, 0.085, 0.045), 0.4,
                              axis="Z", stretch=0.12, coat=0.25)
    M["Plaster"] = B.mat_plain("MAT_PLASTER_WARM", (0.62, 0.58, 0.52), rough=0.85, spec=0.3)
    M["CeilingW"] = B.mat_plain("MAT_CEILING_WHITE", (0.74, 0.72, 0.68), rough=0.9, spec=0.3)
    M["Upholstery"] = B.mat_fabric("MAT_UPHOLSTERY_IVORY", (0.64, 0.60, 0.53), rough=0.9, sheen=0.5)
    M["Mullion"] = B.mat_plain("MAT_MULLION_BRONZE", (0.03, 0.025, 0.02), rough=0.4, metal=0.8)
    M["Glazing"] = B.mat_glass("MAT_GLAZING")
    M["Art"] = mat_image("MAT_ART_WEDDING_01", ART_IMAGE)
    M["Gallery"] = B.mat_plain("MAT_ART_MOUNT_WHITE", (0.8, 0.79, 0.76), rough=0.9)
    M["Skyline"] = mat_skyline("MAT_BLUE_HOUR_SKYLINE")
    M["Tower"] = mat_tower("MAT_TOWER_WINDOWS")
    M["CityGround"] = mat_city_ground("MAT_CITY_GROUND")
    M["Proxy"] = B.mat_plain("MAT_CAST_PROXY_GREY", (0.35, 0.35, 0.36), rough=0.7)
    M["ProxyIsha"] = B.mat_plain("MAT_CAST_PROXY_ISHA_GOWN", (0.02, 0.02, 0.02), rough=0.6)
    M["ProxyVeer"] = B.mat_plain("MAT_CAST_PROXY_VEER_SUIT", (0.04, 0.04, 0.045), rough=0.6)
    M["Studio"] = mat_studio_backdrop("MAT_STUDIO_GRADIENT")
    M["Candle"] = B.mat_plain("MAT_CANDLE_WAX", (0.85, 0.82, 0.74), rough=0.5, sss=0.4)
    M["Flame"] = B.mat_flame("MAT_CANDLE_FLAME")
    M["Bronze"] = B.mat_plain("MAT_BRONZE_SATIN", (0.35, 0.22, 0.1), rough=0.35, metal=1.0)


def mat_travertine(name):
    m, n, l, b = B._mat(name)
    mp = B._coords(n)
    st = n.new("ShaderNodeMapping")
    st.inputs["Scale"].default_value = (1.0, 1.0, 6.0)      # bedding streaks run horizontally
    l.new(mp.outputs[0], st.inputs["Vector"])
    wv = n.new("ShaderNodeTexNoise")
    wv.inputs["Scale"].default_value = 3.5
    wv.inputs["Detail"].default_value = 6.0
    wv.inputs["Distortion"].default_value = 0.6
    l.new(st.outputs[0], wv.inputs["Vector"])
    ramp = B._ramp(n, (0.48, 0.42, 0.33), (0.70, 0.64, 0.54), (0.3, 0.75))
    l.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    pores = n.new("ShaderNodeTexVoronoi")
    pores.inputs["Scale"].default_value = 160.0
    l.new(mp.outputs[0], pores.inputs["Vector"])
    pr = n.new("ShaderNodeMapRange")
    pr.inputs["From Min"].default_value = 0.0
    pr.inputs["From Max"].default_value = 0.05
    pr.inputs["To Min"].default_value = 0.0
    pr.inputs["To Max"].default_value = 1.0
    l.new(pores.outputs["Distance"], pr.inputs["Value"])
    dark = n.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.blend_type = "MULTIPLY"
    l.new(pr.outputs["Result"], dark.inputs["Factor"])
    dark.inputs["Factor"].default_value = 1.0
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(pr.outputs["Result"], inv.inputs[1])
    mm = n.new("ShaderNodeMix")
    mm.data_type = "RGBA"
    l.new(inv.outputs[0], mm.inputs["Factor"])
    l.new(ramp.outputs["Color"], mm.inputs["A"])
    mm.inputs["B"].default_value = (0.30, 0.26, 0.2, 1)
    oi = n.new("ShaderNodeObjectInfo")
    tint = n.new("ShaderNodeMix")
    tint.data_type = "RGBA"
    tint.blend_type = "MULTIPLY"
    tint.inputs["Factor"].default_value = 1.0
    tr = B._ramp(n, (0.93, 0.92, 0.9), (1.05, 1.04, 1.02))
    l.new(oi.outputs["Random"], tr.inputs["Fac"])
    l.new(mm.outputs["Result"], tint.inputs["A"])
    l.new(tr.outputs["Color"], tint.inputs["B"])
    l.new(tint.outputs["Result"], b.inputs["Base Color"])
    B._set(b, rough=0.55, spec=0.4)
    B._bump(n, l, inv.outputs[0], b, 0.15, 0.0008)
    m.diffuse_color = (0.65, 0.6, 0.5, 1)
    return m


def mat_image(name, path):
    m, n, l, b = B._mat(name)
    img = bpy.data.images.load(path, check_existing=True)
    img.name = "ART_WEDDING_01_ANIMATIC_PLACEHOLDER"
    tx = n.new("ShaderNodeTexImage")
    tx.image = img
    tc = n.new("ShaderNodeTexCoord")
    l.new(tc.outputs["UV"], tx.inputs["Vector"])
    l.new(tx.outputs["Color"], b.inputs["Base Color"])
    B._set(b, rough=0.35, spec=0.35, coat=0.3, coat_rough=0.15)   # semi-gloss photographic print
    return m


def mat_skyline(name):
    """Blue-hour sky: deep blue zenith to a warm-grey horizon glow, emission only."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.remove(n["Principled BSDF"])
    tc = n.new("ShaderNodeTexCoord")
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sp.inputs[0])
    rp = n.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (0.32, 0.28, 0.34, 1)
    rp.color_ramp.elements[1].position = 0.55
    rp.color_ramp.elements[1].color = (0.035, 0.07, 0.19, 1)
    l.new(sp.outputs["Z"], rp.inputs["Fac"])
    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 3.0
    l.new(rp.outputs["Color"], em.inputs["Color"])
    l.new(em.outputs[0], n["Material Output"].inputs["Surface"])
    return m


def mat_tower(name):
    """Distant towers: dark facades with a per-window random grid of warm/cool lit windows.
    Windows are 1.5 m bays x 3.3 m floors with mullion and spandrel gaps on every vertical face (the horizontal
    coordinate is x + y, which varies along any face of an axis-aligned box); ~35 % lit at varied brightness, and a
    faint facade glow so the tower silhouettes read against the sky."""
    m, n, l, b = B._mat(name)
    B._set(b, base=(0.012, 0.015, 0.022), rough=0.4, spec=0.6)
    tc = n.new("ShaderNodeTexCoord")
    sep0 = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep0.inputs[0])
    hz = n.new("ShaderNodeMath")
    hz.operation = "ADD"
    l.new(sep0.outputs["X"], hz.inputs[0])
    l.new(sep0.outputs["Y"], hz.inputs[1])
    uv = n.new("ShaderNodeCombineXYZ")
    l.new(hz.outputs[0], uv.inputs["X"])
    l.new(sep0.outputs["Z"], uv.inputs["Y"])
    sc_ = n.new("ShaderNodeVectorMath")
    sc_.operation = "MULTIPLY"
    sc_.inputs[1].default_value = (1.0 / 1.5, 1.0 / 3.3, 0.0)     # 1.5 m bays, 3.3 m floor-to-floor
    l.new(uv.outputs[0], sc_.inputs[0])
    fl = n.new("ShaderNodeVectorMath")
    fl.operation = "FLOOR"
    l.new(sc_.outputs[0], fl.inputs[0])
    fr = n.new("ShaderNodeVectorMath")
    fr.operation = "FRACTION"
    l.new(sc_.outputs[0], fr.inputs[0])
    wn = n.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    l.new(fl.outputs[0], wn.inputs["Vector"])
    lit = n.new("ShaderNodeMath")
    lit.operation = "GREATER_THAN"
    lit.inputs[1].default_value = 0.65
    l.new(wn.outputs["Value"], lit.inputs[0])
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(fr.outputs[0], sep.inputs[0])
    fz = n.new("ShaderNodeMath")                     # spandrel: lit only in the lower 62 % of each floor
    fz.operation = "LESS_THAN"
    fz.inputs[1].default_value = 0.62
    l.new(sep.outputs["Y"], fz.inputs[0])
    fx = n.new("ShaderNodeMath")                     # mullion gap between bays
    fx.operation = "LESS_THAN"
    fx.inputs[1].default_value = 0.78
    l.new(sep.outputs["X"], fx.inputs[0])
    m1 = n.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    l.new(lit.outputs[0], m1.inputs[0])
    l.new(fz.outputs[0], m1.inputs[1])
    mask = n.new("ShaderNodeMath")
    mask.operation = "MULTIPLY"
    l.new(m1.outputs[0], mask.inputs[0])
    l.new(fx.outputs[0], mask.inputs[1])
    wn2 = n.new("ShaderNodeTexWhiteNoise")           # per-window brightness 0.25-1.0
    wn2.noise_dimensions = "4D"
    wn2.inputs["W"].default_value = 7.3
    l.new(fl.outputs[0], wn2.inputs["Vector"])
    br = n.new("ShaderNodeMapRange")
    br.inputs["To Min"].default_value = 0.25
    l.new(wn2.outputs["Value"], br.inputs["Value"])
    m2 = n.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    l.new(mask.outputs[0], m2.inputs[0])
    l.new(br.outputs[0], m2.inputs[1])
    col = B._ramp(n, (1.0, 0.70, 0.40), (0.75, 0.85, 1.0), (0.45, 0.55))
    l.new(wn.outputs["Color"], col.inputs["Fac"])
    mul = n.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    l.new(col.outputs["Color"], mul.inputs["A"])
    l.new(m2.outputs[0], mul.inputs["B"])
    add = n.new("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    add.inputs["Factor"].default_value = 1.0
    add.inputs["B"].default_value = (0.012, 0.016, 0.028, 1.0)     # facade glow
    l.new(mul.outputs["Result"], add.inputs["A"])
    l.new(add.outputs["Result"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.0
    return m


def mat_city_ground(name):
    """Low-rise city below the towers: near-black ground with sparse warm points (0.6 m lights on a 4 m grid, ~15 % of cells lit)."""
    m, n, l, b = B._mat(name)
    B._set(b, base=(0.006, 0.007, 0.010), rough=0.8, spec=0.2)
    tc = n.new("ShaderNodeTexCoord")
    sc_ = n.new("ShaderNodeVectorMath")
    sc_.operation = "MULTIPLY"
    sc_.inputs[1].default_value = (1.0 / 4.0, 1.0 / 4.0, 0.0)
    l.new(tc.outputs["Object"], sc_.inputs[0])
    fl = n.new("ShaderNodeVectorMath")
    fl.operation = "FLOOR"
    l.new(sc_.outputs[0], fl.inputs[0])
    wn = n.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    l.new(fl.outputs[0], wn.inputs["Vector"])
    lit = n.new("ShaderNodeMath")
    lit.operation = "GREATER_THAN"
    lit.inputs[1].default_value = 0.85
    l.new(wn.outputs["Value"], lit.inputs[0])
    fr = n.new("ShaderNodeVectorMath")
    fr.operation = "FRACTION"
    l.new(sc_.outputs[0], fr.inputs[0])
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(fr.outputs[0], sp.inputs[0])
    pt = n.new("ShaderNodeMath")                     # point: corner 0.15 x 0.15 of each cell
    pt.operation = "MAXIMUM"
    l.new(sp.outputs["X"], pt.inputs[0])
    l.new(sp.outputs["Y"], pt.inputs[1])
    pm = n.new("ShaderNodeMath")
    pm.operation = "LESS_THAN"
    pm.inputs[1].default_value = 0.15
    l.new(pt.outputs[0], pm.inputs[0])
    lm = n.new("ShaderNodeMath")
    lm.operation = "MULTIPLY"
    l.new(lit.outputs[0], lm.inputs[0])
    l.new(pm.outputs[0], lm.inputs[1])
    col = B._ramp(n, (1.0, 0.62, 0.30), (1.0, 0.85, 0.65), (0.85, 1.0))
    l.new(wn.outputs["Value"], col.inputs["Fac"])
    mul = n.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    l.new(col.outputs["Color"], mul.inputs["A"])
    l.new(lm.outputs[0], mul.inputs["B"])
    l.new(mul.outputs["Result"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 3.0
    return m


def mat_studio_backdrop(name):
    """Deep charcoal to walnut vertical gradient on a curved sweep."""
    m, n, l, b = B._mat(name)
    tc = n.new("ShaderNodeTexCoord")
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sp.inputs[0])
    rp = B._ramp(n, (0.010, 0.0085, 0.0075), (0.075, 0.042, 0.022), (0.15, 0.95))
    l.new(sp.outputs["Z"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], b.inputs["Base Color"])
    B._set(b, rough=0.85, spec=0.2)
    return m


# ---------------------------------------------------------------- product master + instances
def build_product_master(studio):
    _TARGET["scene"] = studio
    top = coll("01_GLISS_PRODUCT_MASTER")
    mount = coll("GLISS_MASTER_MOUNT", top)
    head = coll("GLISS_MASTER_HEAD", top)
    rootob = bpy.data.objects.new("GLISS_MASTER_ROOT", None)
    rootob.empty_display_type = "ARROWS"
    rootob.empty_display_size = 0.05
    top.objects.link(rootob)
    reg = GP.default_register()
    rootob["dimension_register_json"] = json.dumps(reg)
    rootob["verified_manufacturer_information"] = json.dumps({
        "product": "Gliss COB Surface Track Light (BLACK HSG)", "housing": "Black",
        "body_material": "Aluminium", "electrical_power_watts": 7, "technology": "Recessed COB",
        "illumination": "Focused anti-glare", "installation": "Ceiling or wall", "warm_white_kelvin": 3000,
        "source": "polycab.com p-64543 (fetched 2026-11-27): Specifications 3000K Warm White, Wattage 7"})
    for k, v in GLISS_PREVIEW.items():
        rootob["preview_" + k] = v
    rootob["preview_photometry_warning"] = ("Beam angle and light output are artistic preview assumptions, not "
                                            "Polycab specifications; no IES file supplied. 7 W is electrical "
                                            "input and is NOT used as Cycles radiant power.")
    mats = {k: M[k] for k in ("MAT_BLACK_ALUMINIUM", "MAT_REFLECTOR_ALUMINIUM", "MAT_COB_PHOSPHOR")}
    GP.rebuild_gliss_product(reg, mats)
    for o in list(mount.objects) + list(head.objects):
        o.parent = None
    mount.instance_offset = (0, 0, 0)
    head.instance_offset = (0, 0, 0)
    # keep the master out of every render: excluded in the studio view layer (instances still render)
    exclude(studio.view_layers[0], "01_GLISS_PRODUCT_MASTER")
    # the rebuild function travels with the .blend
    txt = bpy.data.texts.new("gliss_product.py")
    txt.from_string(open(os.path.join(HERE, "gliss_product.py")).read())
    return mount, head


def fixture(name, loc, cname, target=None, tilt_pan=None, light=True, on_keys=((1, 0.0),)):
    """Collection-instance pair (mount + head) + spot light on the optical axis. Returns (mount, head, spot)."""
    mi = bpy.data.objects.new(name + "_MOUNT", None)
    mi.instance_type = "COLLECTION"
    mi.instance_collection = bpy.data.collections["GLISS_MASTER_MOUNT"]
    mi.location = loc
    link(mi, cname)
    hi = bpy.data.objects.new(name + "_HEAD", None)
    hi.instance_type = "COLLECTION"
    hi.instance_collection = bpy.data.collections["GLISS_MASTER_HEAD"]
    hi.parent = mi
    link(hi, cname)
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    hi.location = (0, 0, -root["pivot_depth_m"])
    bpy.context.view_layer.update()
    if target is not None:
        GP.aim_fixture(mi, hi, target)
    elif tilt_pan is not None:
        hi.rotation_euler = (tilt_pan[0], 0, 0)
        mi.rotation_euler = (0, 0, tilt_pan[1])
    sp = None
    if light:
        ld = bpy.data.lights.new(name + "_SPOT", "SPOT")
        ld.color = B.kelvin_rgb(GLISS_PREVIEW["cct_k"])
        ld.spot_size = math.radians(GLISS_PREVIEW["beam_angle_deg"])
        ld.spot_blend = GLISS_PREVIEW["beam_blend"]
        ld.shadow_soft_size = 0.0065
        ld.energy = 0.0
        sp = bpy.data.objects.new(name + "_SPOT", ld)
        sp.parent = hi
        sp.location = Vector(root["emitter_head_local_m"]) + Vector((0, 0, -0.0015))
        link(sp, cname)
        # light output is a per-light custom property (preview assumption) multiplied by the keyed on/off state;
        # the beam angle lives on the light data (spot_size) and is mirrored in beam_angle_deg for the register
        sp["light_output_w"] = GLISS_PREVIEW["light_output_w"]
        sp["beam_angle_deg"] = GLISS_PREVIEW["beam_angle_deg"]
        sp["status"] = "PROVISIONAL preview photometry (no IES)"
        sp["on"] = 0.0
        fc = ld.driver_add("energy")
        d = fc.driver
        d.type = "SCRIPTED"
        for vn, prop in (("on", "on"), ("out", "light_output_w")):
            v = d.variables.new()
            v.name, v.type = vn, "SINGLE_PROP"
            v.targets[0].id = sp
            v.targets[0].data_path = '["%s"]' % prop
        d.expression = "on*out"
    hi["cob_on"] = 0.0
    for f, val in on_keys:
        hi["cob_on"] = val
        hi.keyframe_insert('["cob_on"]', frame=f)
        if sp is not None:
            sp["on"] = val
            sp.keyframe_insert('["on"]', frame=f)
    constant(hi)
    if sp is not None:
        constant(sp)
    return mi, hi, sp


# ---------------------------------------------------------------- studio scene
def build_studio(studio):
    _TARGET["scene"] = studio
    c = "04_PRODUCT_STUDIO"
    coll(c)
    # product: ceiling orientation, housing tilted toward camera-left; stands in space against the sweep
    mi, hi, sp = fixture("GLISS_STUDIO", (0, 0, 1.30), c, tilt_pan=(math.radians(48), math.radians(150)),
                         light=True, on_keys=((1, 0.0), (277, 1.0)))
    sp["light_output_w"] = 1.2       # studio: just enough to glow the reflector edge, no wall spill dominance
    # sweep backdrop
    bm = bmesh.new()
    prof = [(1.2 + 1.4 * math.sin(math.pi / 2 * i / 24), -0.2 + 1.4 * (1 - math.cos(math.pi / 2 * i / 24)))
            for i in range(25)]
    prof = [(-4.0, -0.2)] + prof + [(2.6, 4.0)]
    grid = []
    for x in (-3.0, 3.0):
        grid.append([bm.verts.new((x, y, z)) for y, z in prof])
    for j in range(len(prof) - 1):
        bm.faces.new((grid[0][j], grid[1][j], grid[1][j + 1], grid[0][j + 1]))
    ob = B.mesh_obj("STUDIO_Sweep", bm, c, M["Studio"], True)
    ob.location = (0, 0.4, 0)          # sweep floor runs toward the -Y cameras and rises behind the product
    # lights: large softbox key, narrow champagne rim strip, restrained neutral fill
    for name, loc, tgt, sx, sy, k, p in (
            ("LGT_STUDIO_KEY_SOFTBOX", (-1.1, -0.9, 2.0), (0, 0, 1.25), 1.2, 0.9, 5000, 110.0),
            ("LGT_STUDIO_RIM_CHAMPAGNE", (0.75, 0.55, 1.55), (0, 0, 1.24), 0.06, 1.1, 3600, 70.0),
            ("LGT_STUDIO_FILL", (0.9, -1.4, 1.1), (0, 0, 1.25), 1.0, 1.0, 5200, 10.0)):
        lt = B.light(name, "AREA", loc, p, c, k=k, size=sx, size_y=sy)
        lt.rotation_euler = (Vector(tgt) - lt.location).to_track_quat("-Z", "Y").to_euler()
        lt.visible_camera = False
        if "RIM" in name:
            lt.data.color = (1.0, 0.86, 0.66)
    # macro kicker: large dim card behind the shot-2 camera so the faceted reflector has something to mirror
    front, emit, centre, axis, R = product_points()
    kp = emit + axis * 0.9
    lt = B.light("LGT_STUDIO_MACRO_CARD", "AREA", kp, 0.0, c, k=5000, size=0.9, size_y=0.6)
    lt.rotation_euler = (emit - kp).to_track_quat("-Z", "Y").to_euler()
    lt.visible_camera = False
    for f, v in ((1, 0.0), (37, 3.0), (61, 0.0)):
        lt.data.energy = v
        lt.data.keyframe_insert("energy", frame=f)
    constant(lt.data)
    return mi, hi


# ---------------------------------------------------------------- architecture
def build_architecture(arch):
    _TARGET["scene"] = arch
    c = "02_ARCHITECTURAL_ENVIRONMENT"
    coll(c)
    t = 0.2
    WY0, WY1 = 0.35, 5.75
    B.box("ARCH_Floor_Subfloor", RX0 - t, RX1 + t, RY0 - t, RY1 + t, -0.12, -0.02, M["CeramicDark"], c)
    # oak planks 180 x 1800, staggered, running along Y (into the room)
    k = 0
    x = RX0
    col = 0
    while x < RX1 - 1e-6:
        x1 = min(x + 0.18, RX1)
        y = RY0 - (0.6 * (col % 3))
        while y < RY1 - 1e-6:
            y0, y1 = max(y, RY0), min(y + 1.8, RY1)
            if y1 - y0 > 0.02:
                B.box("ARCH_Floor_Plank_%03d" % k, x + 0.0008, x1 - 0.0008, y0 + 0.0008, y1 - 0.0008, -0.02, 0.0,
                      M["Oak"], c, bev=0.0015, seg=1)
                k += 1
            y += 1.8
        x = x1
        col += 1
    B.box("ARCH_Floor_Joint_Fill", RX0, RX1, RY0, RY1, -0.021, -0.0185, M["CeramicDark"], c)
    B.box("ARCH_Wall_Back_Structure", RX0 - t, RX1 + t, RY0 - t - 0.06, RY0 - 0.06, 0, CEIL + 0.2, M["Plaster"], c)
    B.box("ARCH_Wall_Front", RX0 - t, RX1 + t, RY1, RY1 + t, 0, CEIL + 0.2, M["Plaster"], c)
    B.box("ARCH_Wall_Right", RX1, RX1 + t, RY0 - 0.06, RY1, 0, CEIL + 0.2, M["Plaster"], c)
    B.box("ARCH_Wall_Left_Pier_A", RX0 - t, RX0, RY0 - 0.06, WY0, 0, CEIL + 0.2, M["Plaster"], c)
    B.box("ARCH_Wall_Left_Pier_B", RX0 - t, RX0, WY1, RY1, 0, CEIL + 0.2, M["Plaster"], c)
    B.box("ARCH_Ceiling", RX0 - t, RX1 + t, RY0 - t, RY1 + t, CEIL, CEIL + 0.12, M["CeilingW"], c)
    B.box("ARCH_Skirting_Right", RX1 - 0.012, RX1, RY0, RY1, 0, 0.08, M["Walnut"], c)
    B.box("ARCH_Skirting_Front", RX0, RX1, RY1 - 0.012, RY1, 0, 0.08, M["Walnut"], c)
    # glazing: floor-to-ceiling, bronze mullions every ~1.35 m, transom-free
    B.box("ARCH_Glazing_Glass", RX0 - 0.09, RX0 - 0.08, WY0, WY1, 0.0, CEIL, M["Glazing"], c)
    n = 4
    for i in range(n + 1):
        y = WY0 + (WY1 - WY0) * i / n
        B.box("ARCH_Glazing_Mullion_%d" % i, RX0 - 0.12, RX0 - 0.04, y - 0.025, y + 0.025, 0.0, CEIL, M["Mullion"], c)
    B.box("ARCH_Glazing_Sill", RX0 - 0.12, RX0, WY0, WY1, 0.0, 0.03, M["Mullion"], c)
    B.box("ARCH_Glazing_Head", RX0 - 0.12, RX0, WY0, WY1, CEIL - 0.04, CEIL, M["Mullion"], c)
    # feature wall: honed travertine slabs 1200 x 600 with 3 mm joints on a dark setting bed
    tx0, tx1 = RX0, 1.90
    B.box("ARCH_Feature_Wall_Bed", tx0, tx1, RY0 - 0.06, RY0 - 0.02, 0, CEIL, M["CeramicDark"], c)
    k = 0
    for row in range(int(math.ceil(CEIL / 0.6))):
        z0, z1 = row * 0.6, min((row + 1) * 0.6, CEIL)
        off = 0.6 if row % 2 else 0.0
        xs = tx0 - off
        while xs < tx1 - 1e-6:
            a, b_ = max(xs, tx0), min(xs + 1.2, tx1)
            if b_ - a > 0.02:
                B.box("ARCH_Travertine_Slab_%03d" % k, a + 0.0015, b_ - 0.0015, RY0 - 0.02, RY0, z0 + 0.0015,
                      z1 - 0.0015, M["Travertine"], c, bev=0.001, seg=1)
                k += 1
            xs += 1.2
    # walnut joinery (right section): full-height frame, five shelves, LED under each, closed base cabinet
    jx0, jx1, jd = 1.90, RX1, 0.42
    B.box("JOIN_Back_Panel", jx0, jx1, RY0 - 0.06, RY0, 0, CEIL, M["WalnutV"], c)
    for i, x in enumerate((jx0, jx1 - 0.03)):
        B.box("JOIN_Side_%d" % i, x, x + 0.03, RY0, RY0 + jd, 0, CEIL, M["WalnutV"], c, bev=0.002)
    B.box("JOIN_Base_Cabinet", jx0 + 0.03, jx1 - 0.03, RY0, RY0 + jd, 0, 0.62, M["Walnut"], c, bev=0.002)
    B.box("JOIN_Base_Shadow_Gap", jx0 + 0.03, jx1 - 0.03, RY0 + jd - 0.005, RY0 + jd + 0.001, 0.30, 0.306,
          M["CeramicDark"], c)
    shelves = (1.10, 1.55, 2.00, 2.45)
    em = B.mat_emit("MAT_JOINERY_LED", 3000, 4.0)
    for i, z in enumerate(shelves):
        B.box("JOIN_Shelf_%d" % i, jx0 + 0.03, jx1 - 0.03, RY0, RY0 + jd - 0.01, z, z + 0.035, M["Walnut"], c,
              bev=0.002)
        s = B.box("JOIN_LED_%d" % i, jx0 + 0.05, jx1 - 0.05, RY0 + jd - 0.05, RY0 + jd - 0.035, z - 0.004, z,
                  em, "07_AMBIENT_LIGHT_RIG")
        s.visible_shadow = False
        lt = B.light("LGT_JOIN_SHELF_%d" % i, "AREA", ((jx0 + jx1) / 2, RY0 + jd - 0.06, z - 0.006), 12.0,
                     "07_AMBIENT_LIGHT_RIG", k=3000, size=jx1 - jx0 - 0.12, size_y=0.02)
    B.box("JOIN_Top", jx0, jx1, RY0, RY0 + jd, CEIL - 0.03, CEIL, M["Walnut"], c)
    # shelf props: books, ceramics
    for i in range(6):
        B.box("PROP_Shelf_Book_%d" % i, 2.2 + 0.03 * i, 2.225 + 0.03 * i, RY0 + 0.08, RY0 + 0.30, 1.135,
              1.135 + 0.22 + 0.02 * (i % 3), M["Book1" if i % 2 else "Book2"], c, bev=0.001)
    B.lathe("PROP_Shelf_Vase", [(0, 0), (0.06, 0), (0.09, 0.14), (0.05, 0.3), (0.0, 0.3)], M["Ceramic"], c,
            loc=(3.0, RY0 + 0.2, 1.585))
    B.lathe("PROP_Shelf_Bowl", [(0, 0), (0.05, 0), (0.12, 0.07), (0.11, 0.075), (0, 0.01)], M["CeramicDark"], c,
            loc=(2.5, RY0 + 0.2, 2.035))
    B.lathe("PROP_Shelf_Sculpture", [(0, 0), (0.04, 0), (0.06, 0.1), (0.02, 0.24), (0, 0.25)], M["Bronze"], c,
            loc=(3.05, RY0 + 0.2, 2.485))
    # artwork 1800 x 1200, 35 mm walnut frame, centre (0, 0.04, 1.65)
    W, H, fd = 1.8, 1.2, 0.035
    cx, cz = 0.0, 1.65
    yf = RY0 + 0.04
    bm = bmesh.new()
    v = [bm.verts.new((cx + sx * (W / 2 - 0.05), yf - 0.004, cz + sz * (H / 2 - 0.05))) for sx, sz in
         ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(v[::-1])
    uv = bm.loops.layers.uv.new()
    for loop in f.loops:
        co = loop.vert.co
        # viewed from +Y, screen-left is +X: map u from +X to -X so the print reads correctly (Isha left)
        loop[uv].uv = (((cx + W / 2 - 0.05) - co.x) / (W - 0.1), (co.z - (cz - H / 2 + 0.05)) / (H - 0.1))
    art = B.mesh_obj("ART_WEDDING_01", bm, c, M["Art"])
    art["image_status"] = ("ANIMATIC PLACEHOLDER: monochrome crop of the master storyboard (176 x 117 px source). "
                           "Replace with the approved ART_WEDDING_01 photograph; same image in every shot.")
    B.box("ART_WEDDING_01_Backing", cx - W / 2 + 0.01, cx + W / 2 - 0.01, RY0, yf - 0.012, cz - H / 2 + 0.01,
          cz + H / 2 - 0.01, M["Gallery"], c)
    fw = 0.035
    for name, (x0, x1, z0, z1) in (("T", (cx - W / 2, cx + W / 2, cz + H / 2 - fw, cz + H / 2)),
                                   ("B", (cx - W / 2, cx + W / 2, cz - H / 2, cz - H / 2 + fw)),
                                   ("L", (cx - W / 2, cx - W / 2 + fw, cz - H / 2, cz + H / 2)),
                                   ("R", (cx + W / 2 - fw, cx + W / 2, cz - H / 2, cz + H / 2))):
        B.box("ART_WEDDING_01_Frame_" + name, x0, x1, RY0, RY0 + fd + 0.005, z0, z1, M["Walnut"], c, bev=0.002)
    # exterior: blue-hour sky dome section + distant towers (constant; no animation)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((-700, -800, -60), (-700, 800, -60), (-700, 800, 500), (-700, -800, 500))]
    bm.faces.new(vs)
    sky = B.mesh_obj("EXT_Sky_Backdrop", bm, c, M["Skyline"])
    sky.visible_shadow = False
    bm = bmesh.new()                                 # low-rise city plane 40 m below the floor (apartment height)
    vs = [bm.verts.new(p) for p in ((-30, -800, -40), (-690, -800, -40), (-690, 800, -40), (-30, 800, -40))]
    bm.faces.new(vs)
    gnd = B.mesh_obj("EXT_City_Ground", bm, c, M["CityGround"])
    gnd.visible_shadow = False
    rnd = 0.41
    for i in range(34):                              # 34 towers, 220-600 m out, gaps of sky between silhouettes
        rnd = (rnd * 9301 + 49297) % 233280 / 233280.0
        dist = 220 + 380 * ((i * 0.618) % 1.0)
        y = math.tan(math.radians(-50 + 100 * (i + 0.5 * rnd) / 34.0)) * dist
        w = 12 + 14 * rnd
        h = 20 + 100 * ((i * 0.37 + rnd) % 1.0) ** 2
        B.box("EXT_Tower_%02d" % i, -dist - w, -dist, y, y + w * 0.8, -40, h, M["Tower"], c)
    # furniture: sofa 2700 x 950 x 800, long axis along Y, back to the glazing
    sx, sy = -2.65, 3.65
    x0, x1, y0, y1 = sx - 0.475, sx + 0.475, sy - 1.35, sy + 1.35
    B.box("SOFA_Plinth", x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, 0.0, 0.08, M["Walnut"], c)
    B.box("SOFA_Seat_Base", x0, x1, y0, y1, 0.08, 0.30, M["Upholstery"], c, bev=0.03, seg=3)
    B.box("SOFA_Back", x0, x0 + 0.24, y0, y1, 0.30, 0.80, M["Upholstery"], c, bev=0.05, seg=4)
    B.box("SOFA_Arm_A", x0 + 0.24, x1, y0, y0 + 0.2, 0.30, 0.60, M["Upholstery"], c, bev=0.05, seg=4)
    B.box("SOFA_Arm_B", x0 + 0.24, x1, y1 - 0.2, y1, 0.30, 0.60, M["Upholstery"], c, bev=0.05, seg=4)
    for i in range(3):
        a, b_ = y0 + 0.2 + i * 0.767, y0 + 0.2 + (i + 1) * 0.767
        B.box("SOFA_Seat_Cushion_%d" % i, x0 + 0.25, x1 - 0.02, a + 0.006, b_ - 0.006, 0.30, 0.44,
              M["Upholstery"], c, bev=0.045, seg=4)
        B.box("SOFA_Back_Cushion_%d" % i, x0 + 0.24, x0 + 0.42, a + 0.01, b_ - 0.01, 0.44, 0.76, M["Upholstery"],
              c, bev=0.06, seg=4)
    # round walnut coffee table 900 x 350
    tx, ty = -1.45, 3.55
    B.cyl("TABLE_Coffee_Top", 0.45, 0.31, 0.35, M["Walnut"], c, loc=(tx, ty), n=128, bev=0.006)
    B.cyl("TABLE_Coffee_Plinth", 0.30, 0.0, 0.31, M["Walnut"], c, loc=(tx, ty), n=96, bev=0.004)
    for i in range(3):
        B.box("PROP_Table_Book_%d" % i, tx - 0.2, tx + 0.04 - 0.02 * i, ty - 0.12, ty + 0.12 - 0.01 * i,
              0.35 + 0.025 * i, 0.374 + 0.025 * i, M["Book1" if i % 2 else "Book2"], c, bev=0.001)
    B.lathe("PROP_Table_Ceramic", [(0, 0), (0.05, 0), (0.08, 0.06), (0.06, 0.14), (0.02, 0.16), (0, 0.16)],
            M["Ceramic"], c, loc=(tx + 0.18, ty - 0.15, 0.35))
    B.lathe("PROP_Candle", [(0, 0), (0.035, 0), (0.035, 0.09), (0, 0.09)], M["Candle"], c,
            loc=(tx + 0.12, ty + 0.18, 0.35))
    fl = B.sphere("PROP_Candle_Flame", 0.008, (tx + 0.12, ty + 0.18, 0.455), M["Flame"], c, scale=(1, 1, 2.2))
    fl.visible_shadow = False
    B.light("LGT_CANDLE", "POINT", (tx + 0.12, ty + 0.18, 0.46), 0.6, "07_AMBIENT_LIGHT_RIG", k=1850, size=0.01)
    # flowers (ivory blooms) in a vase on the joinery base, greenery by the glazing
    B.lathe("PROP_Flower_Vase", [(0, 0), (0.07, 0), (0.09, 0.2), (0.05, 0.34), (0.06, 0.36), (0, 0.36)],
            M["CeramicDark"], c, loc=(2.35, RY0 + 0.22, 0.62))
    for i in range(9):
        a = i * 2.399
        p = (2.35 + 0.08 * math.cos(a), RY0 + 0.22 + 0.06 * math.sin(a), 0.98 + 0.04 * ((i * 0.618) % 1))
        B.sphere("PROP_Flower_%d" % i, 0.045, p, M["Ceramic"], c, scale=(1, 1, 0.8))
    B.plant("PROP_Greenery", (-3.05, 1.15, 0.0), 0.22, 1.6)
    return arch


def build_ambient_lights():
    c = "07_AMBIENT_LIGHT_RIG"
    # existing architectural lighting (constant across before/after): two dim recessed downlights over the seating,
    # a floor lamp at the sofa end, joinery shelf LEDs (above), candle (above)
    for i, (x, y) in enumerate(((-1.6, 2.6), (-1.6, 4.4))):
        B.cyl("FIX_Downlight_Trim_%d" % i, 0.045, CEIL - 0.004, CEIL, M["CeramicDark"], c, loc=(x, y), n=48)
        lt = B.light("LGT_AMBIENT_DOWN_%d" % i, "SPOT", (x, y, CEIL - 0.01), 40.0, c, k=3000, size=0.02, spot=60)
        lt.data.spot_blend = 0.9
    lx, ly = -2.95, 1.55
    B.cyl("FIX_FloorLamp_Base", 0.15, 0.0, 0.02, M["Bronze"], c, loc=(lx, ly), n=48)
    B.cyl("FIX_FloorLamp_Stem", 0.01, 0.02, 1.45, M["Bronze"], c, loc=(lx, ly), n=16)
    B.lathe("FIX_FloorLamp_Shade", [(0.16, 1.32), (0.20, 1.32), (0.17, 1.62), (0.13, 1.62)], M["Shade"], c,
            loc=(lx, ly, 0), smooth=True)
    B.light("LGT_AMBIENT_FLOORLAMP", "POINT", (lx, ly, 1.48), 60.0, c, k=2700, size=0.08)
    pt = B.light("LGT_WINDOW_PORTAL", "AREA", (RX0 - 0.1, 3.05, CEIL / 2), 0.0, c, size=CEIL, size_y=5.4,
                 rot=(0, math.radians(-90), 0))
    pt.data.cycles.is_portal = True


def build_installed(sc, c="03_INSTALLED_GLISS", prefix="GLISS_INSTALLED", on_keys=((1, 0.0), (85, 1.0))):
    """Two installed fixtures. The walkthrough scene gets its own pair (same master geometry, own on-state)."""
    _TARGET["scene"] = sc
    coll(c)
    out = []
    for i, (loc, tgt) in enumerate(FIXTURES):
        mi, hi, sp = fixture("%s_%s" % (prefix, "L" if i == 0 else "R"), loc, c, target=tgt, on_keys=on_keys)
        mi["illumination_target_m"] = tgt
        mi["orientation_status"] = "PROVISIONAL until verified articulation limits are available"
        out.append((mi, hi, sp))
    return out


def build_cast(arch):
    _TARGET["scene"] = arch
    c = "05_CAST_PREVIS"
    coll(c)
    res = []
    for name, (x, y), h, mat, face in (("ISHA_01_PROXY", ISHA, 1.65, M["ProxyIsha"], math.radians(90)),
                                       ("VEER_01_PROXY", VEER, 1.80, M["ProxyVeer"], math.radians(-90))):
        root = B.empty(name, (x, y, 0), c, "SINGLE_ARROW", 0.3)
        root.rotation_euler = (0, 0, face)
        parts = []
        s = h / 1.75
        for pn, r, z0, z1 in (("Legs", 0.12, 0.0, 0.85), ("Torso", 0.17, 0.85, 1.42), ("Neck", 0.05, 1.42, 1.5)):
            o = B.cyl(name + "_" + pn, r * s, z0 * s, z1 * s, mat if pn != "Neck" else M["Proxy"], c, n=24)
            parts.append(o)
        hd = B.sphere(name + "_Head", 0.105 * s, (0, 0, 1.6 * s), M["Proxy"], c, scale=(0.85, 1.0, 1.15))
        parts.append(hd)
        nose = B.box(name + "_FacingMark", -0.01, 0.01, 0.09 * s, 0.12 * s, 1.58 * s, 1.62 * s, M["Proxy"], c)
        parts.append(nose)
        for p in parts:
            p.parent = root
        root["proxy_note"] = ("Correctly scaled blocking proxy only. Does not represent the approved facial "
                              "identity; final performances come from separately supplied character layers.")
        res.append(root)
    # visible only in the present-day shots (6-9): kept out of shots 3-5 so the push-in on the photograph is clear
    for root in res:
        for o in [root] + list(root.children):
            for f, hide in ((1, True), (133, False), (277, True)):
                o.hide_render = hide
                o.keyframe_insert("hide_render", frame=f)
                o.hide_viewport = False
            constant(o)
    return res


# ---------------------------------------------------------------- cameras
def cam_rig(cid, cname, lens, fstop, keys, focus_obj=None, focus_keys=None, orbit=None):
    """<ID>_DOLLY (animated location) -> <ID>_ROLL (Track To <ID>_TARGET) -> <ID> camera (local roll 0).
    keys: [(frame, position, target)]. orbit: (pivot, deg0, deg1, f0, f1) replaces position keys with an eased arc."""
    dolly = B.empty(cid + "_DOLLY", keys[0][1], cname, "CUBE", 0.05)
    tgt = B.empty(cid + "_TARGET", keys[0][2], cname, "SPHERE", 0.02)
    roll = B.empty(cid + "_ROLL", (0, 0, 0), cname, "ARROWS", 0.05)
    roll.parent = dolly
    tc = roll.constraints.new("TRACK_TO")
    tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    cd = bpy.data.cameras.new(cid)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 0.01
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(cid, cd)
    cam.parent = roll
    link(cam, cname)
    cam["roll_deg_note"] = "Horizon roll controller: rotate this camera about local Z (currently 0, unapproved)"
    if orbit:
        piv, a0, a1, f0, f1 = orbit
        pv = B.empty(cid + "_ORBIT", piv, cname, "CIRCLE", 0.1)
        rel = Vector(keys[0][1]) - Vector(piv)
        dolly.parent = pv
        dolly.location = rel
        for f, a in ((f0, a0), (f1, a1)):
            pv.rotation_euler = (0, 0, math.radians(a))
            pv.keyframe_insert("rotation_euler", index=2, frame=f)
        ease(pv)
        for f, _, t in keys:
            tgt.location = t
            tgt.keyframe_insert("location", frame=f)
    else:
        for f, p, t in keys:
            dolly.location = p
            dolly.keyframe_insert("location", frame=f)
            tgt.location = t
            tgt.keyframe_insert("location", frame=f)
        ease(dolly)
    ease(tgt)
    if focus_obj is not None:
        cd.dof.focus_object = focus_obj
    elif focus_keys:
        for f, dist in focus_keys:
            cd.dof.focus_distance = dist
            cd.dof.keyframe_insert("focus_distance", frame=f)
        ease(cd)
    else:
        for f, p, t in keys:
            cd.dof.focus_distance = (Vector(t) - Vector(p)).length
            cd.dof.keyframe_insert("focus_distance", frame=f)
        ease(cd)
    return cam


def product_points():
    """World-space optical centre (front face centre), emitter and housing centre of the studio product."""
    bpy.context.view_layer.update()
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    hi = bpy.data.objects["GLISS_STUDIO_HEAD"]
    mi = bpy.data.objects["GLISS_STUDIO_MOUNT"]
    reg = json.loads(root["dimension_register_json"])
    d = GP.dims_m(reg)
    R = d["housing_outer_diameter"] / 2
    L = d["housing_length"]
    pr = min(d["pivot_offset"], L * 0.6)
    zf = -(L - pr)
    M_ = mi.matrix_basis @ hi.matrix_basis
    front = M_ @ Vector((0, -R, zf))
    emit = M_ @ Vector(root["emitter_head_local_m"])
    centre = M_ @ Vector((0, -R, (pr + zf) / 2))
    axis = (M_.to_3x3() @ Vector((0, 0, -1))).normalized()
    return front, emit, centre, axis, R


def build_studio_cameras(studio):
    _TARGET["scene"] = studio
    c = "06_CINEMATIC_CAMERAS"
    coll(c)
    front, emit, centre, axis, R = product_points()
    # overall product bounds for occupancy (instances evaluated)
    hgt = 0.165
    dist = hgt / (0.65 * 20.25 / 85.0)                      # 65 % of frame height at 85 mm
    eye = Vector((0, -1, 0)).normalized()
    p0 = centre + Matrix.Rotation(math.radians(-6), 3, "Z") @ (Vector((0.25, -1.0, 0.18)).normalized() * dist)
    cams = []
    cams.append(cam_rig("CAM_01_PRODUCT_HERO", c, 85.0, 5.6,
                        [(1, p0, centre), (36, p0, centre)], orbit=(centre, 0.0, 12.0, 1, 36),
                        focus_keys=[(1, (front - p0).length), (36, (front - p0).length)]))
    # macro push-in along the optical axis toward the COB: 0.12 x housing diameter of travel
    start = emit + axis * 0.205
    travel = 0.12 * 2 * R
    end = start - axis * travel
    cams.append(cam_rig("CAM_02_COB_MACRO", c, 100.0, 8.0, [(37, start, emit), (60, end, emit)],
                        focus_keys=[(37, (emit - start).length - 0.006), (60, (emit - end).length - 0.006)]))
    # packshot: static, product on the left third, negative space right for END_01 artwork
    # frame the whole fixture (base top to housing bottom) at ~68 % of frame height, centred vertically,
    # horizontally on the left third
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    mi, hi = bpy.data.objects["GLISS_STUDIO_MOUNT"], bpy.data.objects["GLISS_STUDIO_HEAD"]
    d = GP.dims_m(json.loads(root["dimension_register_json"]))
    L = d["housing_length"]
    pr = min(d["pivot_offset"], L * 0.6)
    M_ = mi.matrix_basis @ hi.matrix_basis
    pts = [M_ @ Vector((sx * R, -R + sy * R, zz)) for sx in (-1, 1) for sy in (-1, 1) for zz in (pr, -(L - pr))]
    rb = d["mounting_base_diameter"] / 2
    pts += [mi.matrix_basis @ Vector((sx * rb, sy * rb, 0.0)) for sx in (-1, 1) for sy in (-1, 1)]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    bc = (lo + hi_) / 2
    ph = hi_.z - lo.z
    pdist = ph / (0.68 * 20.25 / 85.0) + (hi_.y - lo.y) / 2
    fw = 36.0 / 85.0 * pdist
    look = bc + Vector((fw / 6.0, 0.0, 0.0))         # product on the left third, negative space right
    pk = look + Vector((0.0, -pdist, 0.0))
    cams.append(cam_rig("CAM_10_FINAL_PACKSHOT", c, 85.0, 8.0, [(277, pk, look), (360, pk, look)],
                        focus_keys=[(277, (bc - pk).length), (360, (bc - pk).length)]))
    return cams


def build_arch_cameras(arch, installed):
    _TARGET["scene"] = arch
    c = "06_CINEMATIC_CAMERAS"
    coll(c)
    cams = {}
    cams["03"] = cam_rig("CAM_03_AMBIENT", c, 35.0, 5.6, [(61, (0, 3.6, 1.75), (0, 0.04, 1.95)),
                                                          (84, (0, 3.6, 1.75), (0, 0.04, 1.95))])
    # CAM_04 reuses CAM_03: same camera data, parented with an identity transform (cannot drift)
    c4 = bpy.data.objects.new("CAM_04_TRANSFORMATION", cams["03"].data)
    c4.parent = cams["03"]
    link(c4, c)
    c4["camera_source"] = "Reuses CAM_03_AMBIENT: shared camera data and identity parent transform"
    cams["04"] = c4
    cams["05"] = cam_rig("CAM_05_WEDDING_MEMORY", c, 85.0, 5.6, [(109, (0, 2.9, 1.65), (0, 0.04, 1.65)),
                                                                (132, (0, 2.65, 1.65), (0, 0.04, 1.65))])
    cams["06"] = cam_rig("CAM_06_MATCH_CUT", c, 85.0, 4.0, [(133, (0, 5.05, 1.55), (0, 2.0, 1.55)),
                                                           (168, (0, 5.00, 1.55), (0, 2.0, 1.55))])
    eye = (ISHA[0] - 0.035, ISHA[1] + 0.06, 1.55)
    cams["07"] = cam_rig("CAM_07_HUMAN_CONNECTION", c, 85.0, 4.0, [(169, (0.55, 3.35, 1.62), eye),
                                                                  (204, (0.55, 3.30, 1.62), eye)])
    # installed fixture: 8-degree lateral arc about the right fixture's vertical axis, from below-front, clear
    # of the ceiling by >= 0.33 m
    mi, hi, sp = installed[1]
    fx = mi.location.copy()
    tgt8 = fx + Vector((0, 0, -0.06))
    p8 = fx + Vector((0.42, 0.72, -0.40))
    cams["08"] = cam_rig("CAM_08_INSTALLED_GLISS", c, 70.0, 5.6, [(205, p8, tgt8), (228, p8, tgt8)],
                         orbit=(Vector((fx.x, fx.y, p8.z)), -4.0, 4.0, 205, 228),
                         focus_keys=[(205, (tgt8 - p8).length), (228, (tgt8 - p8).length)])
    k9 = [(229, (1.30, 3.10, 1.45), (0, 0.6, 1.65)), (240, (1.40, 3.55, 1.45), (0, 0.6, 1.60)),
          (252, (1.55, 4.15, 1.45), (0, 0.6, 1.58)), (264, (1.65, 4.75, 1.45), (0, 0.6, 1.55)),
          (276, (1.75, 5.20, 1.45), (0, 0.6, 1.55))]
    cams["09"] = cam_rig("CAM_09_ARCHITECTURAL_REVEAL", c, 24.0, 8.0, k9)
    return cams


def build_walkthrough_camera(walk):
    _TARGET["scene"] = walk
    c = "08_WALKTHROUGH_CAMERA"
    coll(c)
    keys = [(1, (2.4, 5.3, 1.55), (0, 0.5, 1.65)), (60, (1.9, 4.6, 1.55), (0, 0.4, 1.65)),
            (120, (1.2, 3.6, 1.55), (0, 0.04, 1.65)), (180, (0.8, 2.6, 1.55), (0, 0.04, 1.65)),
            (240, (0.5, 2.2, 1.55), (0.3, 0.65, 2.65))]
    cam = cam_rig("CAM_WALKTHROUGH", c, 24.0, 8.0, keys)
    # arc-length timing: re-time the location keys so speed is uniform between the ends (eased only at ends)
    dolly = bpy.data.objects["CAM_WALKTHROUGH_DOLLY"]
    segs = [(Vector(keys[i + 1][1]) - Vector(keys[i][1])).length for i in range(len(keys) - 1)]
    total = sum(segs)
    acc = 0.0
    frames = [1]
    for s in segs:
        acc += s
        frames.append(1 + round(239 * acc / total))
    dolly.animation_data_clear()
    tgt = bpy.data.objects["CAM_WALKTHROUGH_TARGET"]
    tgt.animation_data_clear()
    for (f0, p, t), f in zip(keys, frames):
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
    cam["arc_length_key_frames"] = frames
    walk.camera = cam
    return cam


# ---------------------------------------------------------------- render settings, markers, edit
def render_settings(sc, frames):
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "MILLIMETERS"
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = 256
    cy.preview_samples = 32
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.01
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 12, 6, 6, 8
    cy.transparent_max_bounces = 16
    cy.caustics_reflective = cy.caustics_refractive = False
    cy.sample_clamp_indirect = 8.0
    cy.seed = 11
    cy.use_animated_seed = False
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = frames
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    s = sc.render.image_settings
    if hasattr(s, "media_type"):
        s.media_type = "MULTI_LAYER_IMAGE"
    s.file_format = "OPEN_EXR_MULTILAYER"
    s.color_depth = "16"
    s.exr_codec = "DWAA"
    sc.view_settings.view_transform = "AgX"
    looks = [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items]
    want = [x for x in looks if "Medium High Contrast" in x]
    sc.view_settings.look = want[0] if want else "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.view_settings.use_white_balance = False
    for vl in sc.view_layers:
        vl.use_pass_diffuse_direct = vl.use_pass_diffuse_indirect = True
        vl.use_pass_glossy_direct = vl.use_pass_glossy_indirect = True
        vl.use_pass_emit = vl.use_pass_z = vl.use_pass_normal = vl.use_pass_vector = True
        vl.use_pass_cryptomatte_object = vl.use_pass_cryptomatte_material = True


def bind_markers(sc, pairs):
    sc.timeline_markers.clear()
    for f, name, cam in pairs:
        m = sc.timeline_markers.new(name, frame=f)
        m.camera = cam
    sc.camera = pairs[0][2]


def key_gliss(sc, keys):
    for f, v in keys:
        sc["gliss_on"] = v
        sc.keyframe_insert('["gliss_on"]', frame=f)
    constant(sc)


def build_world(sc, name, col, strength):
    w = bpy.data.worlds.get(name) or bpy.data.worlds.new(name)
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*col, 1)
    bg.inputs["Strength"].default_value = strength
    sc.world = w


def build_edit(edit, scenes_by_name, cams):
    edit.render.fps = FPS
    edit.frame_start, edit.frame_end = 1, 360
    edit.render.resolution_x, edit.render.resolution_y = 3840, 2160
    se = edit.sequence_editor_create()
    strips = se.strips
    for (cid, scn, f0, f1), (_, mname) in zip(SHOTS, MARKERS):
        st = strips.new_scene(name=mname, scene=scenes_by_name[scn], channel=1, frame_start=1)
        st.scene_camera = cams[cid]
        st.frame_final_start = f0
        st.frame_final_end = f1 + 1
    for f, name in MARKERS:
        edit.timeline_markers.new(name, frame=f)


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    arch = bpy.context.scene
    arch.name = "SCENE_ARCHITECTURE"
    studio = scene("SCENE_PRODUCT_STUDIO")
    walk = scene("SCENE_WALKTHROUGH_PREVIEW")
    edit = scene("SCENE_MASTER_EDIT")
    _TARGET["scene"] = arch
    build_materials()
    M["Shade"] = B.MAT.get("Shade") or B.mat_plain("MAT_LAMP_SHADE", (0.8, 0.74, 0.62), rough=0.9, sss=0.3)
    mount, head = build_product_master(studio)
    for sc in (arch, walk):
        sc.collection.children.link(bpy.data.collections["01_GLISS_PRODUCT_MASTER"])
        exclude(sc.view_layers[0], "01_GLISS_PRODUCT_MASTER")
    build_studio(studio)
    _TARGET["scene"] = arch
    build_architecture(arch)
    _TARGET["scene"] = arch
    build_ambient_lights()
    installed = build_installed(arch)
    build_cast(arch)
    # walkthrough scene shares the room collections (not the cast)
    for cname in ("02_ARCHITECTURAL_ENVIRONMENT", "07_AMBIENT_LIGHT_RIG"):
        walk.collection.children.link(bpy.data.collections[cname])
    build_installed(walk, "09_WALKTHROUGH_GLISS", "GLISS_WALKTHROUGH", ((1, 1.0),))
    _TARGET["scene"] = arch
    bpy.context.window_manager  # noqa: B018
    scams = build_studio_cameras(studio)
    acams = build_arch_cameras(arch, installed)
    wcam = build_walkthrough_camera(walk)
    for sc, fr in ((studio, (1, 360)), (arch, (1, 360)), (walk, (1, 240))):
        render_settings(sc, fr)
    build_world(arch, "WORLD_BLUE_HOUR", (0.03, 0.06, 0.16), 1.0)
    walk.world = arch.world
    build_world(studio, "WORLD_STUDIO_BLACK", (0.004, 0.004, 0.005), 1.0)
    # arch view layers: BEAUTY (cast excluded, final plates) and PREVIS (cast included, animatic)
    vb = arch.view_layers[0]
    vb.name = "BEAUTY"
    vp = arch.view_layers.new("PREVIS")
    exclude(vb, "05_CAST_PREVIS")
    exclude(vp, "01_GLISS_PRODUCT_MASTER")
    for vl in arch.view_layers:
        vl.use = True
    render_settings(arch, (1, 360))
    vp.use = False       # animatic renders switch PREVIS on and BEAUTY off
    cams = {cid: bpy.data.objects[cid] for cid, *_ in SHOTS}
    bind_markers(studio, [(1, "01_PRODUCT_HERO", cams["CAM_01_PRODUCT_HERO"]),
                          (37, "02_COB_MACRO", cams["CAM_02_COB_MACRO"]),
                          (277, "10_FINAL_PACKSHOT", cams["CAM_10_FINAL_PACKSHOT"])])
    bind_markers(arch, [(f, n, cams[cid]) for (cid, scn, f, _), (_, n) in zip(SHOTS, MARKERS)
                        if scn == "SCENE_ARCHITECTURE"])
    build_edit(edit, {s.name: s for s in (studio, arch)}, cams)
    for sc in (studio, arch, walk):
        sc.frame_set(1)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    print("SAVED", OUT_BLEND, "objects", len(bpy.data.objects))


if __name__ == "__main__":
    main()
