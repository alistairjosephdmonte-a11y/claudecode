"""Builds "The Invisible Force", a 15-second, five-shot film, and saves scenes/polycab_invisible_force.blend.

    blender -b --factory-startup --python scripts/build_invisible_force.py

The living room, fan, remote and hand are the procedural builders from ../polycab_superior_switch/scripts/
build_scene.py, so room geography is identical between the two films. This script adds the five cameras (bound
to markers), studio strip lights for the macro shots, the airflow controller that drives the curtains and plant,
re-timed fan and light cues, and the 11 collections this brief asks for.

Fan and remote are PROXY geometry: no approved catalogue, CAD or remote reference was supplied."""

import math
import os
import sys

import bpy
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "polycab_superior_switch", "scripts"))
import build_scene as B  # noqa: E402

OUT_BLEND = os.path.join(ROOT, "scenes", "polycab_invisible_force.blend")
FPS = 24
FRAMES = (1, 360)
SHOTS = [  # name, first frame, last frame, lens (mm), f-stop
    ("SH01_Macro_Blade", 1, 72, 85.0, 2.8),
    ("SH02_Remote_Press", 73, 120, 85.0, 2.8),
    ("SH03_Fan_Orbit", 121, 216, 40.0, 4.0),
    ("SH04_Curtain_Plant", 217, 288, 50.0, 4.0),
    ("SH05_Hero_Wide", 289, 360, 30.0, 5.6),
]
TIMING = dict(
    thumb_down=108, thumb_up=114,                    # remote press, shot 2
    fan_start=110, fan_ramp=96, fan_rpm=180.0,       # 180 rpm: illustrative preview value from the brief
    wash=(140, 156), perim=(146, 162), cove=(150, 176), shelf=(160, 182), string=(170, 200),
    air=(150, 236),                                  # airflow at the curtains builds after the fan, delayed
)
COLL_MAP = {
    "01_ARCHITECTURE": "01_ARCHITECTURE",
    "02_INTERIOR_ASSETS": "02_FURNITURE_AND_DECOR",
    "03_POLYCAB_AERORUSH": "03_AERORUSH_PRODUCT",
    "04_REMOTE_CONTROL": "04_REMOTE_AND_HAND",
    "05_LIGHTING_FIXTURES": "05_LIGHTING_FIXTURES",
    "06_LIGHT_RIG": "06_LIGHT_RIG",
    "07_CAMERA_RIG": "08_CAMERAS",
    "08_ANIMATION_CONTROLS": "09_ANIMATION_CONTROLS",
    "09_BRANDING": "10_BRANDING",
    "10_RENDER_SETTINGS": "11_RENDER_OUTPUT",
}
COLLS = ["01_ARCHITECTURE", "02_FURNITURE_AND_DECOR", "03_AERORUSH_PRODUCT", "04_REMOTE_AND_HAND",
         "05_LIGHTING_FIXTURES", "06_LIGHT_RIG", "07_CURTAIN_AND_PLANT", "08_CAMERAS", "09_ANIMATION_CONTROLS",
         "10_BRANDING", "11_RENDER_OUTPUT"]
_orig_coll = B.coll
B.coll = lambda name: _orig_coll(COLL_MAP.get(name, name))

FX, FY = B.FAN_XY
BLADE_Z = B.TRAY - 0.238 - 0.064


def ease(fcurves_owner):
    for fc in B.fcurves_of(fcurves_owner):
        for kp in fc.keyframe_points:
            if fc.data_path == "hide_render":
                continue
            kp.interpolation = "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        fc.update()


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def switch_keys(idb, path, value, f_on, f_off):
    """Constant-interpolated on/off keys: value from f_on up to f_off - 1, zero elsewhere."""
    for f, v in ((1, 0.0), (f_on, value), (f_off, 0.0)):
        if f == 1 and f_on == 1:
            continue
        setattr(idb, path, v)
        idb.keyframe_insert(path, frame=f)
    for fc in B.fcurves_of(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def visible_only(objs, f_on, f_off):
    for o in objs:
        for f, hide in ((1, True), (f_on, False), (f_off, True)):
            o.hide_render = hide
            o.keyframe_insert("hide_render", frame=f)
        for fc in B.fcurves_of(o):
            if fc.data_path == "hide_render":
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def new_camera(name, lens, fstop):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 0.01
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(name, cd)
    B.link(cam, "07_CAMERA_RIG")
    return cam


def tracked(cam, keys, focus=None):
    """keys: (frame, camera location, look-at point). Focus distance follows the look-at point unless given."""
    tgt = B.empty(cam.name + "_Target", keys[0][2], "07_CAMERA_RIG", "SPHERE", 0.03)
    tc = cam.constraints.new("TRACK_TO")
    tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    for f, loc, t in keys:
        cam.location = loc
        cam.keyframe_insert("location", frame=f)
        tgt.location = t
        tgt.keyframe_insert("location", frame=f)
        cam.data.dof.focus_distance = (Vector(t) - Vector(loc)).length if focus is None else focus
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    for idb in (cam, tgt, cam.data):
        ease(idb)
    return tgt


# ======================================================================== cameras
def build_cameras():
    cams = []
    # SH01: macro track along blade 1's underside from mid-span to the motor housing; fan still
    c1 = new_camera("CAM_SH01_Macro", 85.0, 2.8)
    tracked(c1, [(1, (FX + 0.95, FY - 0.42, BLADE_Z - 0.22), (FX + 0.42, FY, BLADE_Z)),
                 (72, (FX + 0.45, FY - 0.34, BLADE_Z - 0.20), (FX + 0.08, FY, BLADE_Z + 0.01))])
    cams.append(c1)
    # SH02: close-up on the remote, looking up past it toward the (defocused) fan
    c2 = new_camera("CAM_SH02_Remote", 85.0, 2.8)
    tracked(c2, [(73, (0.42, -1.05, 1.22), (FX, FY, BLADE_Z - 0.1)),
                 (120, (0.40, -1.02, 1.235), (FX, FY, BLADE_Z - 0.1))], focus=0.50)
    cams.append(c2)
    # SH03: low-angle 60-degree orbit about the fan axis, rising slightly
    c3 = new_camera("CAM_SH03_Orbit", 40.0, 4.0)
    piv = B.empty("CAM_SH03_Orbit_Pivot", (FX, FY, 0.0), "07_CAMERA_RIG", "CIRCLE", 0.3)
    c3.parent = piv
    for f, a, z in ((121, -32.0, 1.08), (216, 28.0, 1.28)):
        piv.rotation_euler = (0, 0, math.radians(a))
        piv.keyframe_insert("rotation_euler", index=2, frame=f)
        c3.location = (0.0, -1.55, z)
        c3.keyframe_insert("location", frame=f)
    for fc in B.fcurves_of(piv):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO"
            kp.easing = "AUTO"
        fc.keyframe_points[0].handle_left_type = "VECTOR"
        fc.update()
    ease(c3)
    t3 = B.empty("CAM_SH03_Orbit_Target", (FX, FY, BLADE_Z - 0.06), "07_CAMERA_RIG", "SPHERE", 0.03)
    tc = c3.constraints.new("TRACK_TO")
    tc.target = t3
    tc.track_axis = "TRACK_NEGATIVE_Z"
    tc.up_axis = "UP_Y"
    c3.data.dof.focus_object = t3
    cams.append(c3)
    # SH04: sheer curtain and plant by the window, slow lateral drift
    c4 = new_camera("CAM_SH04_Curtain", 50.0, 4.0)
    tracked(c4, [(217, (-0.55, -1.32, 1.15), (-2.25, 0.02, 1.20)),
                 (288, (-0.63, -1.24, 1.19), (-2.25, 0.14, 1.22))], focus=1.85)
    cams.append(c4)
    # SH05: wide architectural hero, dolly back and rise, settling to a still end frame
    c5 = new_camera("CAM_SH05_Hero", 30.0, 5.6)
    tracked(c5, [(289, (0.03, -2.05, 1.42), (-0.25, 0.95, 2.05)),
                 (350, (0.05, -2.74, 1.58), (-0.25, 1.05, 1.95)),
                 (360, (0.05, -2.76, 1.585), (-0.25, 1.05, 1.95))])
    cams.append(c5)
    sc = bpy.context.scene
    sc.timeline_markers.clear()
    for cam, (name, f0, f1, lens, fs) in zip(cams, SHOTS):
        m = sc.timeline_markers.new(name, frame=f0)
        m.camera = cam
        cam["shot"] = name
        cam["frames"] = "%d-%d" % (f0, f1)
    sc.camera = cams[0]
    return cams


# ======================================================================== remote + hand (shot 2)
def build_hand_rig(cam, remote_root, hover, press):
    c = "04_REMOTE_CONTROL"
    rig = B.empty("HAND_Rig_SH02", (0, 0, 0), c, "CUBE", 0.03)
    rig.parent = cam
    remote_root.parent = rig
    remote_root.rotation_euler = Euler((math.radians(-64), math.radians(-10), math.radians(-24)), "XYZ")
    # camera-space path: rises into frame, settles with a slight natural drift, small dip on the click
    t = TIMING
    keys = [(73, (0.020, -0.140, -0.52)), (86, (0.006, -0.052, -0.50)), (98, (0.002, -0.046, -0.498)),
            (t["thumb_down"], (0.000, -0.048, -0.497)), (t["thumb_down"] + 1, (0.000, -0.0495, -0.4985)),
            (t["thumb_up"], (0.000, -0.048, -0.497)), (120, (-0.003, -0.042, -0.496))]
    for f, loc in keys:
        rig.location = loc
        rig.keyframe_insert("location", frame=f)
    ease(rig)
    for f, hv, pr in ((t["thumb_down"] - 4, 1.0, 0.0), (t["thumb_down"], 0.0, 1.0), (t["thumb_up"] - 1, 0.0, 1.0),
                      (t["thumb_up"] + 3, 1.0, 0.0)):
        hover.value, press.value = hv, pr
        hover.keyframe_insert("value", frame=f)
        press.keyframe_insert("value", frame=f)
    ease(hover.id_data)
    visible_only([rig] + list(rig.children_recursive), SHOTS[1][1], SHOTS[2][1])
    return rig


# ======================================================================== studio strips for shots 1-2
def build_studio_strips():
    c = "06_LIGHT_RIG"
    strips = []
    for name, loc, target, sx, sy, power in (
            ("LGT_Studio_Strip_Under", (FX + 0.40, FY + 0.75, BLADE_Z - 0.55), (FX + 0.35, FY, BLADE_Z), 1.10,
             0.10, 24.0),
            ("LGT_Studio_Strip_Rim", (FX + 0.35, FY + 0.35, BLADE_Z + 0.20), (FX + 0.25, FY - 0.1, BLADE_Z), 0.9,
             0.04, 6.0),
            ("LGT_Studio_Softbox_Key", (FX + 0.45, FY - 0.85, BLADE_Z - 0.75), (FX + 0.30, FY, BLADE_Z), 0.7, 0.35,
             4.0),
            ("LGT_Studio_Hand_Key", (0.05, -1.25, 1.75), (0.30, -0.70, 1.30), 0.6, 0.25, 9.0)):
        lt = B.light(name, "AREA", loc, power, c, k=4000 if "Hand" not in name else 3400, size=sx, size_y=sy)
        aim(lt, target)
        lt.visible_camera = False
        lt["purpose"] = "macro product strip light, shots 1-2 only"
        strips.append((lt, power))
    for lt, power in strips:
        on, off = (SHOTS[1][1], SHOTS[2][1]) if "Hand" in lt.name else (1, SHOTS[2][1])
        switch_keys(lt.data, "energy", power, on, off)
    return strips


# ======================================================================== airflow: curtains + plant
def build_airflow():
    """CTRL_Airflow.level (0..1) is the airflow reaching the window wall: a smoothstep that starts after the fan
    and lags it. Curtains and leaves are displaced by slowly travelling noise scaled by that level and by a
    height/radius weight, so the motion is soft, delayed and bounded (no simulation, so no instability)."""
    c = "08_ANIMATION_CONTROLS"
    a0, a1 = TIMING["air"]
    ctrl = B.empty("CTRL_Airflow", (B.RX0 + 0.6, 0.6, 2.2), c, "SINGLE_ARROW", 0.2)
    ctrl["start_frame"], ctrl["full_frame"] = float(a0), float(a1)
    ctrl["sheer_amp_m"], ctrl["panel_amp_m"], ctrl["leaf_amp_m"] = 0.07, 0.012, 0.018
    ctrl["level"] = 0.0
    fc = ctrl.driver_add('["level"]')
    d = fc.driver
    d.type = "SCRIPTED"
    for n, p in (("a", "start_frame"), ("b", "full_frame")):
        v = d.variables.new()
        v.name, v.type = n, "SINGLE_PROP"
        v.targets[0].id = ctrl
        v.targets[0].data_path = '["%s"]' % p
    u = "min(max((frame-a)/(b-a),0),1)"
    d.expression = "%s*%s*(3-2*%s)" % (u, u, u)
    # travelling noise origin (air drifting up the wall and along it)
    flow = B.empty("CTRL_Airflow_Noise_Origin", (B.RX0, 0.0, 0.0), c, "PLAIN_AXES", 0.1)
    for f, loc in ((1, (B.RX0, 0.0, 0.0)), (360, (B.RX0, 3.0, 6.0))):
        flow.location = loc
        flow.keyframe_insert("location", frame=f)
    for fc in B.fcurves_of(flow):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    cc = "07_CURTAIN_AND_PLANT"
    for name, amp_key, size, mid, direction in (("CURTAIN_Sheer", "sheer_amp_m", 0.55, 0.0, "X"),
                                                ("CURTAIN_Panel_Front", "panel_amp_m", 0.7, 0.5, "X"),
                                                ("CURTAIN_Panel_Back", "panel_amp_m", 0.7, 0.5, "X"),
                                                ("PLANT_Window_Front_Foliage", "leaf_amp_m", 0.35, 0.5, "NORMAL"),
                                                ("PLANT_Right_Foliage", "leaf_amp_m", 0.35, 0.5, "NORMAL")):
        ob = bpy.data.objects[name]
        # weight: curtains move most at the hem, leaves most at their tips (distance from the trunk)
        vg = ob.vertex_groups.new(name="AIR_Weight")
        if name.startswith("CURTAIN"):
            for v in ob.data.vertices:
                h = 1.0 - min(max(v.co.z / B.CEIL, 0.0), 1.0)
                vg.add([v.index], h ** 1.4, "REPLACE")
        else:
            cx, cy = sum(v.co.x for v in ob.data.vertices) / len(ob.data.vertices), \
                sum(v.co.y for v in ob.data.vertices) / len(ob.data.vertices)
            rmax = max(math.hypot(v.co.x - cx, v.co.y - cy) for v in ob.data.vertices)
            for v in ob.data.vertices:
                vg.add([v.index], min(1.0, math.hypot(v.co.x - cx, v.co.y - cy) / rmax) ** 1.5, "REPLACE")
        tex = bpy.data.textures.new("TEX_Air_" + name, "CLOUDS")
        tex.noise_scale = size
        tex.noise_depth = 1
        tex.noise_basis = "BLENDER_ORIGINAL"
        m = ob.modifiers.new("Airflow", "DISPLACE")
        m.texture = tex
        m.texture_coords = "OBJECT"
        m.texture_coords_object = flow
        m.direction = direction
        m.mid_level = mid
        m.vertex_group = "AIR_Weight"
        m.strength = 0.0
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
        fd = m.driver_add("strength").driver
        fd.type = "SCRIPTED"
        for n, p in (("lv", "level"), ("amp", amp_key)):
            v = fd.variables.new()
            v.name, v.type = n, "SINGLE_PROP"
            v.targets[0].id = ctrl
            v.targets[0].data_path = '["%s"]' % p
        # curtains are pushed toward the window (-X), away from the string lights hung in front of them
        fd.expression = "-lv*amp" if name.startswith("CURTAIN") else "lv*amp"
        for col in list(ob.users_collection):
            col.objects.unlink(ob)
        B.coll(cc).objects.link(ob)
    return ctrl


def move_to(prefixes, cname):
    for o in bpy.data.objects:
        if o.name.startswith(prefixes):
            for col in list(o.users_collection):
                col.objects.unlink(o)
            B.coll(cname).objects.link(o)


def mark_proxies():
    for name, what in (("FAN_Mount", "Aerorush fan geometry rebuilt from public product photos"),
                       ("REMOTE_Root", "neutral placeholder remote; no approved remote reference supplied")):
        ob = bpy.data.objects[name]
        ob["PROXY_NOT_PRODUCT_ACCURATE"] = what
    for name, cname, loc in (("PROXY_LABEL_Fan_Not_Product_Accurate", "03_POLYCAB_AERORUSH", (FX, FY, B.TRAY - 0.5)),
                             ("PROXY_LABEL_Remote_Placeholder", "04_REMOTE_CONTROL", (0.3, -0.6, 1.0))):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = "PROXY: not product-accurate" if "Fan" in name else "PROXY remote: placeholder"
        cu.size = 0.05
        ob = bpy.data.objects.new(name, cu)
        ob.location = loc
        ob.hide_render = True
        B.link(ob, cname)


def render_settings(cams):
    B.LENS = SHOTS[4][3]
    B.render_settings()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.frame_start, sc.frame_end = FRAMES
    sc.cycles.samples = 48
    # partial white balance toward the 3000 K practicals: warm, but not orange
    sc.view_settings.use_white_balance = True
    sc.view_settings.white_balance_temperature = 4400
    sc.view_settings.white_balance_tint = -5
    doc = bpy.data.objects["RENDER_Settings_Doc"]
    for k, v in (("resolution", "3840x2160"), ("frames", "1-360"), ("samples", 48), ("white_balance", "4400 K, tint -5"),
                 ("shots", "; ".join("%s %d-%d %gmm f/%g" % s for s in SHOTS))):
        doc[k] = v
    B.build_branding(cams[4])


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for cname in COLLS:
        B.coll(cname)
    B.TIMING = TIMING
    B.FPS = FPS
    B.FRAMES = FRAMES
    B.build_materials()
    B.build_architecture()
    B.build_feature_wall()
    B.sofa()
    B.coffee_table()
    B.side_table_lamp()
    B.curtains()
    B.console_shelves()
    B.build_lights()
    fan_root, rotor, blades = B.build_fan()
    remote = B.build_remote()
    hand, hover, press = B.build_hand(remote)
    cams = build_cameras()
    build_hand_rig(cams[1], remote, hover, press)
    build_studio_strips()
    B.build_controls(rotor)
    build_airflow()
    move_to(("CURTAIN_", "PLANT_"), "07_CURTAIN_AND_PLANT")
    mark_proxies()
    render_settings(cams)
    sc = bpy.context.scene
    sc.frame_set(1)
    for c in bpy.data.collections:
        if c.name not in COLLS:
            raise RuntimeError("unexpected collection " + c.name)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
    print("SAVED", OUT_BLEND, "objects", len(bpy.data.objects))


main()
