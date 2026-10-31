"""Camera rigs: one dedicated camera per shot, full-frame 36 mm sensor, motivated moves only.
Lenses: 28 mm establishing, 35 mm interiors, 50 mm details, 85 mm evidence, orthographic for graphics/document layouts."""
import math

import bpy
from mathutils import Vector

import assets as A


def _ease(o):
    from bpy_extras import anim_utils
    ad = o.animation_data
    if not ad or not ad.action:
        return
    for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
        for k in fc.keyframe_points:
            k.interpolation = "BEZIER"
            k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
        fc.update()


def camera(name, coll_, f0, f1, path, aim=None, lens=35.0, ortho=None, fstop=None, focus=None, fixed_rot=None, move="dolly"):
    """path: [(frame, (x,y,z))] (two keys = start/end of a single motivated move), aim: [(frame, (x,y,z))] or fixed_rot.
    ortho: (scale_start, scale_end) for orthographic graphics cameras."""
    cd = bpy.data.cameras.new(name)
    cd.sensor_width, cd.sensor_fit = 36.0, "HORIZONTAL"
    cd.clip_start, cd.clip_end = 0.02, 3000.0
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho[0]
        cd.keyframe_insert("ortho_scale", frame=f0)
        cd.ortho_scale = ortho[1]
        cd.keyframe_insert("ortho_scale", frame=f1)
        _ease(cd)
    else:
        cd.lens = lens
    cam = A.obj(name, cd, coll_, path[0][1])
    cam["move"] = move
    cam["lens_mm"] = 0 if ortho else lens
    if fixed_rot is not None:
        cam.rotation_euler = fixed_rot
    else:
        tgt = A.empty(f"{name}_AIM", coll_, aim[0][1], 0.1, "SPHERE")
        con = cam.constraints.new("TRACK_TO")
        con.target, con.track_axis, con.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
        for f, p in aim:
            tgt.location = p
            tgt.keyframe_insert("location", frame=f)
        _ease(tgt)
    for f, p in path:
        cam.location = p
        cam.keyframe_insert("location", frame=f)
    _ease(cam)
    if fstop and not ortho:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if isinstance(focus, (int, float)):
            cd.dof.focus_distance = focus
        elif focus is not None:
            cd.dof.focus_object = focus
    return cam


def frame_half_extent(cam, depth):
    """Half width/height of the frame at `depth` metres in front of the camera (16:9)."""
    cd = cam.data
    hw = cd.ortho_scale / 2 if cd.type == "ORTHO" else depth * 18.0 / cd.lens
    return hw, hw * 9 / 16


def overhead(name, coll_, f0, f1, center0, center1, height, ortho=None, lens=50.0, yaw=0.0):
    """Top-down camera (fixed rotation, so it can never flip)."""
    return camera(name, coll_, f0, f1, [(f0, (center0[0], center0[1], height)), (f1, (center1[0], center1[1], height))],
                  fixed_rot=(0, 0, yaw), lens=lens, ortho=ortho, move="overhead")


def front_ortho(name, coll_, f0, f1, origin, scale=(16.0, 15.2), drift=(0.0, 0.0)):
    """Graphics stage camera: looks +Y at the stage plane, orthographic, a restrained push (scale) and optional drift."""
    o = Vector(origin)
    return camera(name, coll_, f0, f1, [(f0, tuple(o + Vector((0, -20, 0)))), (f1, tuple(o + Vector((drift[0], -20, drift[1]))))],
                  fixed_rot=(math.radians(90), 0, 0), ortho=scale, move="graphics_push")
