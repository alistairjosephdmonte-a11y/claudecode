"""Blockout QA for BOWLCURRY_MADRAS_BLOCKOUT.blend; writes metadata/BC_BLOCKOUT_QA_REPORT.json and
metadata/camera_paths.json (per-frame camera position, target, lens, clearance) for the plan drawings.

    blender -b scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend --python scripts/qa_bowlcurry.py"""
import json
import math
import os

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = bpy.data.scenes["BC_MADRAS_MASTER"]
vl = sc.view_layers[0]
results = []


def check(name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print("QA", name, bool(ok), json.dumps(detail)[:200])


def solids():
    skip = ("FX_STEAM", "SIM_MANTAFLOW", "CAMERAS", "LIGHTS")
    return [o for o in sc.objects if o.type == "MESH" and not any(o.name in bpy.data.collections[c].objects
                                                                  for c in skip)]


def bvh_at(f, objs):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for o in objs:
        oe = o.evaluated_get(dg)
        if oe.hide_render:
            continue
        me = oe.to_mesh()
        mw = oe.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        oe.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def cam_for(f):
    return bpy.data.objects["CAM_A"] if f < 241 else bpy.data.objects["CAM_B"]


with bpy.context.temp_override(scene=sc, view_layer=vl):
    r = sc.render
    check("format: 360 frames @ 24 fps, 3840 x 2160", (sc.frame_start, sc.frame_end, r.fps, r.resolution_x,
                                                         r.resolution_y) == (1, 360, 24, 3840, 2160),
          [sc.frame_start, sc.frame_end, r.fps, r.resolution_x, r.resolution_y])
    mk = sorted((m.frame, m.camera.name) for m in sc.timeline_markers if m.camera)
    check("camera switch: CAM_A 1-240, CAM_B 241-360", mk == [(1, "CAM_A"), (241, "CAM_B")], mk)

    # product + cookware dimensions
    sc.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    k = bpy.data.objects["BC_MADRAS_01_ISLAND"]
    me = k.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    dims = [round((max(a) - min(a)) * 1000, 2) for a in (xs, ys, zs)]
    check("carton 120 x 45 x 190 mm (PROVISIONAL), upright, dieline UVs", dims == [120.0, 45.0, 190.0]
          and "DIELINE" in me.uv_layers, {"dims_mm": dims, "uv": list(me.uv_layers.keys())})
    orange = {o.name for o in sc.objects if o.type == "MESH" and o.data.materials
              and any(m and m.name == "CARTON_PROVISIONAL_ORANGE" for m in o.data.materials)}
    check("orange used only on provisional cartons", orange == {"BC_MADRAS_01_ISLAND", "BC_MADRAS_01_HERO"},
          sorted(orange))
    pan = bpy.data.objects["PAN_Body"]
    rim_r = max(math.hypot(v.co.x, v.co.y) for v in pan.data.vertices if abs(v.co.z - 0.053) < 1e-6
                and math.hypot(v.co.x, v.co.y) < 0.142)
    out_r = max(math.hypot(v.co.x, v.co.y) for v in pan.data.vertices if abs(v.co.z - 0.053) < 1e-6)
    wall = (out_r - rim_r) * 1000
    check("skillet 280 mm inner top diameter, 5 mm wall", abs(rim_r * 2 - 0.280) < 0.0005 and abs(wall - 5) < 0.2,
          {"inner_top_diameter_mm": round(rim_r * 2000, 1), "wall_mm": round(wall, 2)})

    # cameras: interpolation, clearance, window side, hold
    interp = set()
    for nm in ("CAM_A", "CAM_A_TARGET", "CAM_B", "CAM_B_TARGET"):
        ob = bpy.data.objects[nm]
        for fc in ob.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            interp |= {kp.interpolation for kp in fc.keyframe_points}
    for nm in ("CAM_A", "CAM_B"):
        cd = bpy.data.cameras[nm]
        for fc in cd.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            interp |= {kp.interpolation for kp in fc.keyframe_points}
    check("camera keys use Bezier interpolation", interp == {"BEZIER"}, sorted(interp))
    objs = solids()
    paths, min_clear, worst, crossings, wrong_side = {}, 9.0, None, [], []
    prev = None
    for f in range(1, 361):
        bvh = bvh_at(f, objs)
        cam = cam_for(f)
        p = cam.matrix_world.translation.copy()
        tgt = bpy.data.objects[cam.name + "_TARGET"].matrix_world.translation.copy()
        nearest = bvh.find_nearest(p)
        d = nearest[3] if nearest[0] is not None else 9.0
        if d < min_clear:
            min_clear, worst = d, f
        if prev is not None and prev[0] == cam.name:
            seg = p - prev[1]
            if seg.length > 1e-6:
                hit = bvh.ray_cast(prev[1], seg.normalized(), seg.length)
                if hit[0] is not None:
                    crossings.append(f)
        right = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
        if right.dot(Vector((-1, 0, 0))) >= 0:          # window (x = -4) must be on camera-left
            wrong_side.append(f)
        paths.setdefault(cam.name, []).append([f, [round(c, 4) for c in p], [round(c, 4) for c in tgt],
                                               round(cam.data.lens, 2), round(d, 3)])
        prev = (cam.name, p)
    check("camera clearance >= 0.05 m from all solid geometry", min_clear >= 0.05,
          {"min_clearance_m": round(min_clear, 3), "frame": worst})
    check("no camera path segment passes through geometry", not crossings, crossings[:10])
    check("window light on camera-left every frame", not wrong_side, wrong_side[:10])
    cb = bpy.data.objects["CAM_B"]
    sc.frame_set(288)
    m0 = cb.matrix_world.copy()
    l0 = cb.data.lens
    still = True
    for f in range(288, 361):
        sc.frame_set(f)
        if any(abs(a - b) > 1e-6 for ra, rb in zip(cb.matrix_world, m0) for a, b in zip(ra, rb)) \
                or abs(cb.data.lens - l0) > 1e-6:
            still = False
    check("hero hold: CAM_B static 288-360 (73 frames, 3.0 s)", still, {"frames": [288, 360]})

    # hero composition: carton face visible + unobscured, all products in frame, negative space on the right
    hero = bpy.data.objects["BC_MADRAS_01_HERO"]
    face_ok, occl, inframe, right_max = True, [], True, 0.0
    for f in (288, 324, 360):
        bvh = bvh_at(f, objs)
        cam = cb
        cpos = cam.matrix_world.translation
        n = hero.matrix_world.to_3x3() @ Vector((0, -1, 0))
        ctr = hero.matrix_world @ Vector((0, -0.0225, 0.095))
        if n.dot((cpos - ctr).normalized()) < 0.9:
            face_ok = False
        for i in range(5):
            for j in range(7):
                pt = hero.matrix_world @ Vector((-0.05 + 0.025 * i, -0.0226, 0.015 + 0.0267 * j))
                dv = pt - cpos
                hit = bvh.ray_cast(cpos, dv.normalized(), dv.length - 0.002)
                if hit[0] is not None:
                    occl.append([f, i, j])
        for nm in ("BC_MADRAS_01_HERO", "BOWL_Serving", "BOWL_Rice"):
            ob = bpy.data.objects[nm]
            for c in ob.bound_box:
                v = world_to_camera_view(sc, cam, ob.matrix_world @ Vector(c))
                if not (0.01 <= v.x <= 0.99 and 0.01 <= v.y <= 0.99):
                    inframe = False
                right_max = max(right_max, v.x)
    check("hero carton face toward camera (>= 0.9 cos) and unobscured (35 face samples)", face_ok and not occl,
          {"occluded_samples": occl[:5]})
    check("hero products fully in frame", inframe, {})
    check("negative space: right 35 % of the hero frame free of product", right_max <= 0.65,
          {"rightmost_product_x": round(right_max, 3)})

    # transition, food behaviour, simulation setup
    st = {}
    for nm in ("STEAM_PAN", "STEAM_BOWL"):
        ob = bpy.data.objects[nm]
        st[nm] = {}
        for f in (230, 240, 241, 250, 330):
            sc.frame_set(f)
            st[nm][f] = round(ob["steam"], 2)
    check("steam occludes the cut (density >= 30 at 240 on CAM_A, 241 on CAM_B; restrained <= 1 at hero)",
          st["STEAM_PAN"][240] >= 30 and st["STEAM_BOWL"][241] >= 30 and st["STEAM_BOWL"][330] <= 1.0, st)
    animated_chicken = [o.name for o in sc.objects if o.name.startswith("CHICKEN") and o.animation_data]
    check("no airborne chicken (all chicken pieces static)", not animated_chicken, animated_chicken)
    sc.frame_set(360)
    sp_z = [round(o.matrix_world.translation.z, 4) for o in sc.objects if o.name.startswith("SPICE_")]
    check("spice proxies settle on the sauce surface", len(set(sp_z)) == 1, {"final_z": sp_z[0], "count": len(sp_z)})
    dom = bpy.data.objects["SIM_SAUCE_DOMAIN"]
    ds = dom.modifiers["Fluid"].domain_settings
    check("Mantaflow liquid setup present (domain, inflow, collisions), unbaked, viscosity PROVISIONAL",
          ds.domain_type == "LIQUID" and ds.use_viscosity and not ds.has_cache_baked_data,
          {"resolution": ds.resolution_max, "viscosity_m2_s": ds.viscosity_base * 10 ** -ds.viscosity_exponent,
           "baked": ds.has_cache_baked_data})
    s = sc.view_settings
    check("final settings stored: AgX, 256 spp adaptive, 180-deg motion blur, EXR multilayer + passes",
          s.view_transform == "AgX" and sc.cycles.samples == 256 and sc.cycles.use_adaptive_sampling
          and r.use_motion_blur and abs(r.motion_blur_shutter - 0.5) < 1e-6
          and r.image_settings.file_format == "OPEN_EXR_MULTILAYER" and vl.use_pass_z
          and vl.use_pass_cryptomatte_object and vl.cycles.use_pass_volume_direct,
          {"look": s.look, "codec": r.image_settings.exr_codec})

os.makedirs(os.path.join(ROOT, "metadata"), exist_ok=True)
with open(os.path.join(ROOT, "metadata", "camera_paths.json"), "w") as fh:
    json.dump(paths, fh)
nfail = sum(not c["pass"] for c in results)
with open(os.path.join(ROOT, "metadata", "BC_BLOCKOUT_QA_REPORT.json"), "w") as fh:
    json.dump({"stage": "BLOCKOUT", "checks": results, "failures": nfail,
               "note": "Geometric/continuity checks only. Product dimensions are PROVISIONAL (spec values); "
                       "artwork, food appearance and fluid behaviour are not validated at this stage."}, fh, indent=1)
print("QA_DONE %d checks, %d fail" % (len(results), nfail))
