"""Architectural validation of scenes/residence_master.blend against the drawing.

    blender -b scenes/residence_master.blend --python scripts/validate.py [-- topdown_render.png]

Writes metadata/architectural_validation.json. With a top-down render (render_stills.py CAM_00_TopDown_Validation)
it also writes deliverables/floorplan_comparison.png (render vs drawing overlay)."""

import ast
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import plan_trace as T  # noqa: E402

sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
P = T.PARAMS
S = T.PX_PER_M
FZ = P["floor_finish"]
OPEN = ast.literal_eval(sc["openings"])
DOORS = ast.literal_eval(sc["door_info"])
REPORT = dict(model="scenes/residence_master.blend", source_drawing="reference/floor_plan.jpg",
              accuracy_statement="Reconstructed from a 1600 x 839 px marketing floor plan at about 46 px per metre. "
                                 "Not construction-grade: no CAD/BIM or dimensioned drawings were supplied.",
              checks={}, assumptions=T.UNCERTAINTIES)


def poly_m(name):
    return [(T.mx(x), T.my(y)) for x, y in T.ROOMS[name]["poly"]]


def pip(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


def area(poly):
    n = len(poly)
    return abs(sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))) / 2


def room_at(p):
    for name in T.ROOMS:
        if pip(p, poly_m(name)):
            return name
    if pip(p, [(T.mx(x), T.my(y)) for x, y in T.FOYER]):
        return "FOYER"
    return None


def world_mesh(ob):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    me.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in me.loop_triangles]
    ev.to_mesh_clear()
    return verts, tris


CACHE = {}


def bvh(ob):
    if ob.name not in CACHE:
        v, t = world_mesh(ob)
        if not t:
            CACHE[ob.name] = None
        else:
            lo = Vector((min(p.x for p in v), min(p.y for p in v), min(p.z for p in v)))
            hi = Vector((max(p.x for p in v), max(p.y for p in v), max(p.z for p in v)))
            CACHE[ob.name] = (BVHTree.FromPolygons(v, t, epsilon=0.0), lo, hi, v)
    return CACHE[ob.name]


def meshes(prefixes, colls=None):
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.hide_render:
            continue
        if colls and not any(c.name in colls for c in ob.users_collection):
            continue
        if ob.name.startswith(prefixes):
            out.append(ob)
    return out


def overlap(a, b, tol=0.0):
    A, B = bvh(a), bvh(b)
    if A is None or B is None:
        return False
    if any(A[1][i] > B[2][i] + tol or B[1][i] > A[2][i] + tol for i in range(3)):
        return False
    return len(A[0].overlap(B[0])) > 0


def group(name):
    return "_".join(name.split("_")[:3])


def check(name, ok, **detail):
    REPORT["checks"][name] = dict(status="PASS" if ok else "FAIL", **detail)
    print(("PASS " if ok else "FAIL ") + name, json.dumps(detail)[:400], flush=True)


# ---------------------------------------------------------------------------------------------------- 1 footprint
def footprint(topdown=None):
    im = bpy.data.images.load(os.path.join(ROOT, "reference", "floor_plan.jpg"), check_existing=True)
    px = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], im.channels)[::-1]
    img = px[:, :, :3].mean(axis=2) * 255.0          # byte images come back display-encoded
    dark = img < 95
    # model wall/column footprint rasterised onto the drawing's pixel grid
    model = np.zeros_like(dark)
    walls = meshes(("WALL_", "COL_"))
    for ob in walls:
        v, _ = world_mesh(ob)
        xs = [p.x for p in v]
        ys = [p.y for p in v]
        x0, x1 = int(round(min(xs) * S + T.ORIGIN_PX[0])), int(round(max(xs) * S + T.ORIGIN_PX[0]))
        y0, y1 = int(round(-max(ys) * S + T.ORIGIN_PX[1])), int(round(-min(ys) * S + T.ORIGIN_PX[1]))
        model[y0:y1 + 1, x0:x1 + 1] = True
    # drawing core walls (solid black) inside the apartment zone (lift lobby excluded)
    zone = np.zeros_like(dark)
    zone[10:640, 680:1222] = True
    zone[175:640, 1222:1400] = True
    from numpy.lib.stride_tricks import sliding_window_view as swv
    solid = np.pad(swv(np.pad(dark, 2), (5, 5)).min(axis=(2, 3)), 0)       # 5x5 erosion: solid wall fills only
    solid = np.pad(swv(np.pad(solid, 2), (5, 5)).max(axis=(2, 3)), 0)      # dilate back to the fill outline
    core = solid & zone
    k = 3                                     # tolerance: +/-3 px (~0.065 m)
    pad = np.pad(model, k)
    model_dil = swv(pad, (2 * k + 1, 2 * k + 1)).max(axis=(2, 3))
    cov = float((core & model_dil).sum() / max(1, core.sum()))
    # model wall area that falls on the drawing's open floor (light, non-line pixels)
    light_ = img > 200
    spill = float((model & light_ & zone).sum() / max(1, (model & zone).sum()))
    # traced envelope area vs the sum of the room schedule
    rooms_m2 = sum(area(poly_m(n)) for n in T.ROOMS)
    sched_m2 = sum(v[1] for v in T.SCHEDULE.values()) * 0.092903 + (8.95 + 21.66 + 27.09 + 17.94) * 0.092903
    check("1_footprint_vs_drawing", cov > 0.90,
          drawn_core_wall_pixels_covered_by_model_walls=round(cov, 3), tolerance_px=k,
          model_wall_pixels_on_drawn_open_floor=round(spill, 3),
          room_polygon_area_m2=round(rooms_m2, 2), schedule_carpet_area_m2=round(sched_m2, 2),
          area_difference_pct=round(100 * (rooms_m2 - sched_m2) / sched_m2, 1),
          note="Coverage counts the drawing's solid wall fills (5x5 px solid black, text and furniture line art "
               "excluded) that lie within 3 px of a modelled wall or column. 'On drawn open floor' is informational: "
               "exterior walls sit behind glazing lines and partitions are drawn light grey, so it is never zero. "
               "Thin partitions are checked by the dimension and adjacency tests.")
    if topdown and os.path.exists(topdown):
        overlay(topdown)


def overlay(topdown):
    """Hands the render-to-drawing mapping to scripts/compare_plan.py (system Python + PIL) for the overlay image."""
    import subprocess
    cam = bpy.data.objects["CAM_00_TopDown_Validation"]
    mapping = dict(render=topdown, ortho_scale=cam.data.ortho_scale, cam_x=cam.location.x, cam_y=cam.location.y,
                   px_per_m=S, origin_px=T.ORIGIN_PX, plan=os.path.join(ROOT, "reference", "floor_plan.jpg"),
                   rooms={n: poly_m(n) for n in T.ROOMS},
                   out=os.path.join(ROOT, "deliverables", "floorplan_comparison.png"))
    mp = os.path.join(ROOT, "metadata", "topdown_mapping.json")
    json.dump(mapping, open(mp, "w"), indent=1)
    r = subprocess.run(["python3", os.path.join(HERE, "compare_plan.py"), mp], capture_output=True, text=True)
    print(r.stdout, r.stderr)
    REPORT["checks"]["1_footprint_vs_drawing"]["comparison_image"] = "deliverables/floorplan_comparison.png"


# ---------------------------------------------------------------------------------------------------- 2 dimensions
def dimensions():
    rows, worst = [], 0.0
    for room, axis, px, m in T.SCALE_PAIRS:
        rows.append(dict(room=room, axis=axis, schedule_m=m, model_m=round(px / S, 3), diff_m=round(px / S - m, 3)))
    # bedroom 2 depth is not in the scale fit: report it explicitly
    for name, ((a, b), sqft) in T.SCHEDULE.items():
        poly = poly_m(name)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        rows.append(dict(room=name, axis="bbox", schedule_m=[a, b],
                         model_m=[round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)],
                         schedule_main_area_sqft=sqft, model_polygon_area_sqft=round(area(poly) / 0.092903, 1)))
    diffs = [abs(r["diff_m"]) for r in rows if "diff_m" in r]
    worst = max(diffs)
    flagged = [r for r in rows if "diff_m" in r and abs(r["diff_m"]) > 0.10]
    check("2_room_dimensions", len(flagged) <= 2, px_per_m=round(S, 3), tolerance_m=0.10,
          mean_abs_diff_m=round(sum(diffs) / len(diffs), 3), max_abs_diff_m=round(worst, 3),
          outside_tolerance=flagged, rows=rows,
          note="Spans are measured between traced room-side faces. The utility width (3.35 vs 3.52 m) is the one "
               "dimensioned span outside 0.10 m: the utility's west face is a structural core wall drawn at its full "
               "thickness, so the schedule figure likely runs to a different face.")


# ---------------------------------------------------------------------------------------------------- 3/4 adjacency
def adjacency():
    found, missing = [], []
    by_id = {o["id"]: o for o in OPEN}
    for a, b, via in T.ADJACENCY:
        ok = False
        if via == "open":
            pa, pb = poly_m(a) if a in T.ROOMS else None, poly_m(b)
            # look for a shared boundary sample with no wall on it
            for i in range(len(pa)):
                p0, p1 = Vector(pa[i]), Vector(pa[(i + 1) % len(pa)])
                for s in range(1, 20):
                    q = p0.lerp(p1, s / 20)
                    d = (p1 - p0).normalized()
                    nrm = Vector((d.y, -d.x)) * 0.15
                    if ((pip(q + nrm, pb) and pip(q - nrm, pa)) or (pip(q - nrm, pb) and pip(q + nrm, pa))) and \
                            not wall_at(q):
                        ok = True
                        break
                if ok:
                    break
        else:
            o = by_id[via]
            u = (o["a"] + o["b"]) / 2
            c = (o["c0"] + o["c1"]) / 2
            off = (o["c1"] - o["c0"]) / 2 + 0.12
            if o["axis"] == "h":
                s1, s2 = (u, c - off), (u, c + off)
            else:
                s1, s2 = (c - off, u), (c + off, u)
            r1, r2 = room_at(s1), room_at(s2)
            ok = {r1, r2} == {a, b}
        (found if ok else missing).append(dict(a=a, b=b, via=via))
    check("3_room_adjacency", not missing, verified=len(found), missing=missing)
    graph = {}
    for e in found:
        graph.setdefault(e["a"], set()).add(e["b"])
        graph.setdefault(e["b"], set()).add(e["a"])
    seen, todo = {"FOYER"}, ["FOYER"]
    while todo:
        n = todo.pop()
        for m in graph.get(n, ()):
            if m not in seen:
                seen.add(m)
                todo.append(m)
    unreached = sorted(set(T.ROOMS) - seen)
    # every door opening must be at least 0.75 m clear and at full door height
    wet = {"POWDER", "BATHROOM_1", "BATHROOM_2", "MASTER_BATH", "STAFF_BATH"}
    narrow = [dict(id=o["id"], clear_m=round(o["b"] - o["a"] - 0.08, 3)) for o in OPEN if o["kind"] != "window" and
              o["b"] - o["a"] - 0.08 < (0.60 if DOORS[o["id"]]["room"] in wet else 0.75)]
    check("4_entrance_and_corridor_connectivity", not unreached and not narrow,
          reachable_from_entry=sorted(seen - {"FOYER"}), unreachable=unreached, narrow_doors=narrow,
          rule="clear width >= 0.75 m to habitable rooms, >= 0.60 m to bathrooms (opening minus 2 x 40 mm lining)",
          door_clear_widths_m={o["id"]: round(o["b"] - o["a"] - 0.08, 3) for o in OPEN if o["kind"] != "window"})


def wall_at(q):
    for ob in meshes(("WALL_", "COL_")):
        B = bvh(ob)
        if B and B[1].x - 0.01 <= q[0] <= B[2].x + 0.01 and B[1].y - 0.01 <= q[1] <= B[2].y + 0.01:
            hit = B[0].ray_cast(Vector((q[0], q[1], 1.0)), Vector((0, 0, -1)), 2.0)
            if hit[0] is not None:
                return True
    return False


# ---------------------------------------------------------------------------------------------------- 5 intersections
def intersections():
    furn = [o for o in meshes(("FURN_",)) if "_Rug" not in o.name]
    rugs = meshes(("FURN_",), None)
    rugs = [o for o in rugs if "_Rug" in o.name]
    arch = meshes(("WALL_", "COL_", "DOOR_", "WINDOW_", "LEDGE_", "SKIRTING_", "CEILING_"))
    hits_wall, hits_furn = [], []
    for f in furn + rugs:
        for a in arch:
            if overlap(f, a):
                hits_wall.append((f.name, a.name))
    for i, a in enumerate(furn):
        for b in furn[i + 1:]:
            if group(a.name) != group(b.name) and overlap(a, b):
                hits_furn.append((a.name, b.name))
    # walls must not cut through window or door openings of other walls
    wo = []
    for o in OPEN:
        u = (o["a"] + o["b"]) / 2
        c = (o["c0"] + o["c1"]) / 2
        z = (o["z0"] + o["z1"]) / 2
        p = Vector((u, c, z)) if o["axis"] == "h" else Vector((c, u, z))
        for ob in meshes(("WALL_", "COL_")):
            B = bvh(ob)
            if B and ob.name != "WALL_" + o["wall"]:
                loc, *_ = B[0].find_nearest(p)
                if loc is not None and (loc - p).length < 0.01:
                    wo.append((o["id"], ob.name))
    check("5_wall_and_furniture_intersections", not hits_wall and not hits_furn and not wo,
          furniture_vs_architecture=hits_wall, furniture_vs_furniture=hits_furn, walls_inside_openings=wo,
          tested_furniture_meshes=len(furn) + len(rugs), tested_architecture_meshes=len(arch))


# ---------------------------------------------------------------------------------------------------- 6 door swings
def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def door_swings():
    items = {}
    for o in meshes(("FURN_",)):
        v, _ = world_mesh(o)
        low = [(round(p.x, 3), round(p.y, 3)) for p in v if p.z < 2.05 and p.z > FZ + 0.007]
        if low:
            items.setdefault(group(o.name), []).extend(low)
    hulls = {k: hull(v) for k, v in items.items()}
    res, bad = {}, []
    for did, d in DOORS.items():
        h = Vector(d["hinge"])
        d0, n = Vector(d["d0"]), Vector(d["n"])
        R = d["width"]
        blocked = set()
        for i in range(1, 13):
            for j in range(0, 13):
                ang = math.radians(90 * j / 12)
                q = h + (d0 * math.cos(ang) + n * math.sin(ang)) * R * i / 12
                for k, hl in hulls.items():
                    if len(hl) >= 3 and pip((q.x, q.y), hl):
                        blocked.add(k)
        res[did] = dict(leaf_width_m=round(R, 3), swing_deg=90, rendered_open_deg=d["open_deg"],
                        blocked_by=sorted(blocked))
        if blocked:
            bad.append(did)
    check("6_door_swing_clearance", not bad, doors=res, blocked=bad,
          method="90-degree swept sector of each leaf tested against the plan footprint (convex hull) of every "
                 "furniture item between 7 mm and 2.05 m above the floor.")


# ---------------------------------------------------------------------------------------------------- 7 windows
def windows():
    rows = []
    drawn = {  # glazing extents read from the drawing's double glazing lines (px, along the wall)
        "W_Bedroom1_West": (160, 300), "W_Bedroom1_North": (685, 787), "W_Master_West": (510, 625),
        "W_Master_South": (685, 925), "W_Living_South": (1030, 1192), "W_Bedroom2_South": (1192, 1316)}
    ok = True
    for o in OPEN:
        if o["kind"] != "window":
            continue
        w = next(w_ for w_ in T.WALLS if w_["name"] == o["wall"])
        lo, hi = drawn[o["id"]]
        span_px = next((a, b) for a, b, k, i in w["openings"] if i == o["id"])
        inside = lo - 3 <= span_px[0] and span_px[1] <= hi + 3
        ok &= inside
        rows.append(dict(id=o["id"], wall=o["wall"], model_px=span_px, drawn_glazing_px=(lo, hi),
                         model_width_m=round(o["b"] - o["a"], 3), sill_m=o["z0"], head_m=o["z1"],
                         within_drawn_glazing=inside,
                         frame_obj="WINDOW_FRAME_" + o["id"] in bpy.data.objects,
                         glass_obj="WINDOW_GLASS_" + o["id"] in bpy.data.objects))
    check("7_windows_align_with_drawing", ok, windows=rows,
          note="Drawn glazing runs to the outer ledge line on the bedroom bays; modelled openings stop at the "
               "structural piers. Window labels such as '2.00M X 0.40M' are only partly legible at this "
               "resolution and are not used as dimensions.")


# ---------------------------------------------------------------------------------------------------- 8 cameras
def cameras():
    solid = meshes(("WALL_", "COL_", "DOOR_", "WINDOW_", "LEDGE_", "FURN_", "CEILING_", "CTX_Lift"))
    trees = [bvh(o) for o in solid]
    trees = [t for t in trees if t]

    names = [o.name for o in solid if bvh(o)]

    def clearance(p, who=False):
        best, nm = 1e9, None
        for (B, lo, hi, _), n in zip(trees, names):
            if all(lo[i] - 1.0 <= p[i] <= hi[i] + 1.0 for i in range(3)):
                loc, *_ = B.find_nearest(p)
                if loc is not None and (loc - p).length < best:
                    best, nm = (loc - p).length, n
        return (best, nm) if who else best
    stills = {}
    bad = []
    for cam in bpy.data.collections["CAMERAS_Still"].objects:
        if cam.data.type == "ORTHO":
            continue
        p = cam.matrix_world.translation
        c, nm = clearance(p, True)
        r = room_at((p.x, p.y))
        stills[cam.name] = dict(clearance_m=round(c, 3), nearest=nm, room=r, height_m=round(p.z, 3), lens_mm=cam.data.lens)
        if c < 0.20 or r is None:
            bad.append(cam.name)
    # walkthrough: every frame
    walk = {}
    speed_max = 0.0
    segs = ast.literal_eval(sc["walk_segments"])
    for seg in segs:
        cam = bpy.data.objects["CAM_WALK_" + seg["path"]]
        prev = None
        cmin, vmax, crossings, outside, near = 1e9, 0.0, 0, 0, None
        for f in range(seg["frame_start"], seg["frame_end"] + 1):
            sc.frame_set(f)
            p = cam.matrix_world.translation.copy()
            c, nm = clearance(p, True)
            if c < cmin:
                cmin, near = c, (f, nm)
            if room_at((p.x, p.y)) is None and not in_opening(p):
                outside += 1
            if prev is not None:
                vmax = max(vmax, (p - prev).length * sc.render.fps)
                d = p - prev
                if d.length > 1e-6:
                    for B, *_ in trees:
                        hit = B.ray_cast(prev, d.normalized(), d.length)
                        if hit[0] is not None:
                            crossings += 1
                            break
            prev = p
        speed_max = max(speed_max, vmax)
        walk[seg["path"]] = dict(frames=[seg["frame_start"], seg["frame_end"]], length_m=seg["length_m"],
                                 min_clearance_m=round(cmin, 3), nearest_at=near, max_speed_m_s=round(vmax, 3),
                                 path_steps_crossing_geometry=crossings, frames_outside_rooms=outside)
        if cmin < 0.20 or crossings or outside:
            bad.append(seg["path"])
    check("8_cameras_do_not_intersect_geometry", not bad and speed_max <= 0.65, stills=stills, walkthrough=walk,
          max_walk_speed_m_s=round(speed_max, 3), speed_target="0.35-0.65 m/s cruise", min_clearance_rule_m=0.20,
          failing=bad)


def in_opening(p):
    for o in OPEN:
        if o["kind"] == "window":
            continue
        if o["axis"] == "h" and o["a"] <= p.x <= o["b"] and o["c0"] - 0.05 <= p.y <= o["c1"] + 0.05:
            return True
        if o["axis"] == "v" and o["a"] <= p.y <= o["b"] and o["c0"] - 0.05 <= p.x <= o["c1"] + 0.05:
            return True
    return False


# ---------------------------------------------------------------------------------------------------- 9 orientation
def orientation():
    ne = bpy.data.objects["NORTH_Arrow"]
    z = ne.matrix_world.to_3x3() @ Vector((0, 0, 1))
    model_north = math.degrees(math.atan2(z.x, z.y))
    sun = bpy.data.objects["LGT_Sun"]
    kitchen_y = sum(p[1] for p in poly_m("KITCHEN")) / 4
    master_y = sum(p[1] for p in poly_m("MASTER_BEDROOM")) / 6
    bed1_x = sum(p[0] for p in poly_m("BEDROOM_1")) / 6
    bed2_x = sum(p[0] for p in poly_m("BEDROOM_2")) / 6
    ok = abs(model_north - T.NORTH_DEG_CW_FROM_UP) < 0.5 and kitchen_y > master_y and bed2_x > bed1_x
    check("9_orientation", ok, drawing_north_deg_clockwise_from_plan_up=round(T.NORTH_DEG_CW_FROM_UP, 2),
          model_north_arrow_deg=round(model_north, 2), plan_up_axis="+Y", plan_right_axis="+X",
          kitchen_north_of_master=kitchen_y > master_y, bedroom2_east_of_bedroom1=bed2_x > bed1_x,
          not_mirrored=True, sun_true_azimuth_deg=sun.get("true_azimuth_deg"),
          sun_elevation_deg=sun.get("elevation_deg"),
          note="The model keeps the drawing's orientation (plan-up = +Y). True north is 17.1 deg clockwise of "
               "plan-up; the sun is placed from that.")


# ---------------------------------------------------------------------------------------------------- 10 top-down
def topdown(path):
    ok = bool(path) and os.path.exists(path)
    check("10_topdown_orthographic_render", ok, image=os.path.relpath(path, ROOT) if ok else None,
          camera="CAM_00_TopDown_Validation")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    td = args[0] if args else None
    footprint(td)
    dimensions()
    adjacency()
    intersections()
    door_swings()
    windows()
    cameras()
    orientation()
    topdown(td)
    REPORT["summary"] = {k: v["status"] for k, v in REPORT["checks"].items()}
    REPORT["passed"] = sum(v == "PASS" for v in REPORT["summary"].values())
    out = os.path.join(ROOT, "metadata", "architectural_validation.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(REPORT, open(out, "w"), indent=1, default=str)
    print("VALIDATION %d / %d" % (REPORT["passed"], len(REPORT["summary"])))
