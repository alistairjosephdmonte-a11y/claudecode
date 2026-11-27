"""Parametric Gliss COB surface track light: dimension register + rebuild_gliss_product().

Every mesh of the product master is generated from the register. Studio and installed fixtures are collection
instances of the two master sub-collections, so a rebuild updates every copy.

No manufacturer dimensions exist (the official page lists only 7 W, 3000 K warm white, aluminium body, ceiling
or wall mounting). Proportions are fitted to the official product photograph (normalised to housing diameter
1.0); the absolute scale comes from a separate PROVISIONAL world-scale control, seeded from the storyboard
sheet's 60 mm housing diameter (generated imagery, lowest-priority source). When one verified measurement is
supplied, set it in the register and call solve_world_scale(); every other value stays PROVISIONAL until it is
individually replaced.

Mount frame (GLISS_MASTER_MOUNT): mounting face at z = 0, base hangs toward -Z (ceiling orientation), the stem ends
at the pivot. Head frame (GLISS_MASTER_HEAD): origin at the pivot, optical axis along -Z, housing centre line at
y = -R so its side touches the stem tip. Tilt is a rotation of the head about X; pan is a rotation of the mount
about Z."""

import json
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

# relative proportions (housing outer diameter = 1.0), fitted to the official product photograph
# https://cms.polycab.com/media/nsxhpxea/lp0802007bkww-img-01.png (400 x 400 px; housing front ellipse major
# axis ~91 px used as the unit)
PHOTO = "official product photograph (polycab.com p-64543), proportion fit"
STORY = "storyboard sheet (generated imagery), lowest priority"
REGISTER_TEMPLATE = {
    "world_scale_housing_diameter_mm": {"value": 60.0, "status": "PROVISIONAL", "source": STORY,
                                        "note": "World scale control. Not a manufacturer dimension."},
    "relative": {
        "housing_length": (1.75, PHOTO + "; storyboard shows 100/60 = 1.67"),
        "housing_outer_diameter": (1.00, "unit"),
        "housing_wall_thickness": (0.027, PHOTO + " (thin black lip)"),
        "front_rim_thickness": (0.012, PHOTO),
        "cavity_depth": (0.35, PHOTO + " (black sleeve ahead of the reflector)"),
        "reflector_opening_diameter": (0.60, PHOTO),
        "reflector_recess_depth": (0.25, PHOTO),
        "emitter_diameter": (0.22, PHOTO),
        "mounting_base_diameter": (1.07, PHOTO + "; storyboard shows 90 mm = 1.5"),
        "mounting_base_thickness": (0.55, PHOTO + "; storyboard shows 25 mm = 0.42"),
        "boss_diameter": (0.53, PHOTO + " (raised collar where the stem leaves the base)"),
        "boss_height": (0.10, PHOTO),
        "stem_width": (0.30, PHOTO),
        "stem_depth": (0.12, PHOTO),
        "stem_height": (0.60, PHOTO + "; storyboard shows 30 mm = 0.5"),
        "pivot_offset": (0.75, PHOTO + " (pivot distance from housing rear)"),
    },
}
MANUFACTURER_FIELDS = ["housing_length", "housing_outer_diameter", "housing_wall_thickness", "front_rim_thickness",
                       "reflector_opening_diameter", "reflector_recess_depth", "emitter_diameter",
                       "mounting_base_diameter", "mounting_base_thickness", "stem_width", "stem_height",
                       "stem_depth", "pivot_offset", "overall_installed_height"]


def default_register():
    reg = {"world_scale_housing_diameter_mm": dict(REGISTER_TEMPLATE["world_scale_housing_diameter_mm"]),
           "dimensions_mm": {}, "verified_manufacturer_dimensions_mm": {k: None for k in MANUFACTURER_FIELDS}}
    s = reg["world_scale_housing_diameter_mm"]["value"]
    for k, (rel, src) in REGISTER_TEMPLATE["relative"].items():
        reg["dimensions_mm"][k] = {"relative": rel, "value": round(rel * s, 3), "status": "PROVISIONAL",
                                   "source": src}
    return reg


def solve_world_scale(reg):
    """If any verified manufacturer dimension is present, derive the world scale from it (first one wins) and
    refresh every still-provisional value from its relative proportion."""
    for k, v in reg["verified_manufacturer_dimensions_mm"].items():
        if v is not None and k in reg["dimensions_mm"]:
            reg["world_scale_housing_diameter_mm"].update(
                value=v / reg["dimensions_mm"][k]["relative"], status="DERIVED", source="verified " + k)
            break
    s = reg["world_scale_housing_diameter_mm"]["value"]
    for k, d in reg["dimensions_mm"].items():
        ver = reg["verified_manufacturer_dimensions_mm"].get(k)
        if ver is not None:
            d.update(value=ver, status="VERIFIED")
        else:
            d["value"] = round(d["relative"] * s, 3)
    return reg


def dims_m(reg):
    return {k: d["value"] / 1000.0 for k, d in reg["dimensions_mm"].items()}


# ------------------------------------------------------------------ mesh helpers
def _lathe_mesh(name, prof, n, smooth=True, close_axis=True):
    bm = bmesh.new()
    rings = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring = []
        for r, z in prof:
            if r < 1e-9:
                ring.append(None)
            else:
                ring.append((r * math.cos(a), r * math.sin(a), z))
        rings.append(ring)
    axis = {}
    verts = []
    for i in range(n):
        row = []
        for j, (r, z) in enumerate(prof):
            if rings[i][j] is None:
                if j not in axis:
                    axis[j] = bm.verts.new((0, 0, z))
                row.append(axis[j])
            else:
                row.append(bm.verts.new(rings[i][j]))
        verts.append(row)
    for i in range(n):
        a, b = verts[i], verts[(i + 1) % n]
        for j in range(len(prof) - 1):
            q = [a[j], b[j], b[j + 1], a[j + 1]]
            uniq = []
            for v in q:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    return me


def _box_mesh(name, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def _part(name, me, coll, mat, bevel=0.0, seg=2, harden=True):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
    else:
        old = ob.data
        ob.data = me
        if old is not me and old.users == 0:
            bpy.data.meshes.remove(old)
    me.materials.clear()
    me.materials.append(mat)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    if bevel > 0:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width = bevel
        bv.segments = seg
        bv.limit_method = "ANGLE"
        bv.harden_normals = harden
    return ob


# ------------------------------------------------------------------ rebuild
def rebuild_gliss_product(reg=None, mats=None, segments=128):
    """(Re)generate all product master meshes from the register. Returns the register used.
    mats: dict with MAT_BLACK_ALUMINIUM, MAT_REFLECTOR_ALUMINIUM, MAT_COB_PHOSPHOR (looked up by name if None)."""
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    if reg is None:
        reg = json.loads(root["dimension_register_json"])
    reg = solve_world_scale(reg)
    mats = mats or {k: bpy.data.materials[k] for k in ("MAT_BLACK_ALUMINIUM", "MAT_REFLECTOR_ALUMINIUM",
                                                       "MAT_COB_PHOSPHOR")}
    blk, refl, cob = mats["MAT_BLACK_ALUMINIUM"], mats["MAT_REFLECTOR_ALUMINIUM"], mats["MAT_COB_PHOSPHOR"]
    d = dims_m(reg)
    mount = bpy.data.collections["GLISS_MASTER_MOUNT"]
    head = bpy.data.collections["GLISS_MASTER_HEAD"]
    R = d["housing_outer_diameter"] / 2
    L = d["housing_length"]
    t = d["housing_wall_thickness"]
    pr = min(d["pivot_offset"], L * 0.6)    # pivot distance from the housing rear
    zr, zf = pr, -(L - pr)                    # rear / front of the housing along the head's Z axis
    cav = d["cavity_depth"]
    ro = d["reflector_opening_diameter"] / 2
    rd = d["reflector_recess_depth"]
    re = d["emitter_diameter"] / 2
    e = 0.0015                                 # edge radius of the machined housing ends
    # housing: closed rounded rear, thin front lip, black inner sleeve, annular step to the reflector opening,
    # a pocket behind the reflector (hidden). Centre line at y = -R.
    prof = [(0.0, zr), (R - e, zr), (R, zr - e), (R, zf + 0.0006), (R - 0.0004, zf), (R - t, zf),
            (R - t, zf + cav), (ro + 0.0006, zf + cav), (ro + 0.0006, zf + cav + rd + 0.001),
            (0.0, zf + cav + rd + 0.001)]
    me = _lathe_mesh("GLISS_HOUSING", prof, segments)
    hs = _part("GLISS_HOUSING", me, head, blk)
    hs.location = (0, -R, 0)
    # front rim: thin black annulus at the lip (separate part so it can take its own finish)
    rt = d["front_rim_thickness"]
    me = _lathe_mesh("GLISS_FRONT_RIM", [(R - t - 0.0002, zf + 0.0004), (R + 0.0001, zf + 0.0004),
                                         (R + 0.0001, zf - rt + 0.0004), (R - t - 0.0002, zf - rt + 0.0004),
                                         (R - t - 0.0002, zf + 0.0004)], segments)
    rim = _part("GLISS_FRONT_RIM", me, head, blk)
    rim.location = (0, -R, 0)
    # reflector: faceted cone from the opening to the emitter (flat-shaded facets: 36 x 6)
    rings = 6
    prof = [(ro - (ro - re) * k / rings, zf + cav + rd * (k / rings) ** 0.8) for k in range(rings + 1)]
    prof = [(ro + 0.0003, zf + cav)] + prof[1:] + [(re * 0.98, zf + cav + rd), (0.0, zf + cav + rd)]
    me = _lathe_mesh("GLISS_REFLECTOR", prof, 36, smooth=False)
    rf = _part("GLISS_REFLECTOR", me, head, refl)
    rf.location = (0, -R, 0)
    # COB: single circular emitter disc with a very low phosphor dome
    zc = zf + cav + rd - 0.0003
    me = _lathe_mesh("GLISS_COB", [(0.0, zc - 0.0008), (re * 0.6, zc - 0.0006), (re, zc), (0.0, zc)], 64)
    cb = _part("GLISS_COB", me, head, cob)
    cb.location = (0, -R, 0)
    # pivot pad on the housing side where the stem enters (visible seam in the photograph)
    me = _lathe_mesh("GLISS_PIVOT", [(0.0, 0.0), (d["stem_width"] * 0.55, 0.0),
                                     (d["stem_width"] * 0.55, -0.0037), (0.0, -0.0037)], 48)
    pv = _part("GLISS_PIVOT", me, head, blk)
    pv.location = (0, -0.0022, 0)
    pv.rotation_euler = (math.radians(90), 0, 0)        # pad axis along Y, flush with the housing side
    # mount: base drum (soft edges), boss, flat stem ending at the pivot
    Rb, Hb = d["mounting_base_diameter"] / 2, d["mounting_base_thickness"]
    eb = 0.0015
    me = _lathe_mesh("GLISS_BASE", [(0.0, 0.0), (Rb - eb, 0.0), (Rb, -eb), (Rb, -Hb + eb), (Rb - eb, -Hb),
                                    (0.0, -Hb)], segments)
    _part("GLISS_BASE", me, mount, blk)
    rb, hb = d["boss_diameter"] / 2, d["boss_height"]
    me = _lathe_mesh("GLISS_BASE_BOSS", [(0.0, -Hb + 0.0005), (rb, -Hb + 0.0005), (rb, -Hb - hb + 0.0008),
                                         (rb - 0.0008, -Hb - hb), (0.0, -Hb - hb)], segments)
    _part("GLISS_BASE_BOSS", me, mount, blk)
    sw, sd, sh = d["stem_width"], d["stem_depth"], d["stem_height"]
    zp = -(Hb + hb + sh)
    me = _box_mesh("GLISS_STEM", -sw / 2, sw / 2, -sd / 2, sd / 2, zp + 0.0012, -Hb - hb + 0.001)
    _part("GLISS_STEM", me, mount, blk, bevel=0.0012, seg=2)
    # small dark details visible in the photograph: two cover-screw recesses and four vent slots on the drum
    bm = bmesh.new()
    for x in (-Rb * 0.72, Rb * 0.72):
        bmesh.ops.create_circle(bm, cap_ends=True, radius=0.0022, segments=24,
                                matrix=Matrix.Translation((x, 0, -Hb - 0.00005)))
    for k in range(4):
        a = math.radians(-90 + (k - 1.5) * 7.0)
        c, s = math.cos(a), math.sin(a)
        x0, y0 = (Rb + 0.00005) * c, (Rb + 0.00005) * s
        tx, ty = -s, c
        w, h = 0.0007, 0.0028
        vs = [bm.verts.new((x0 + tx * w * sx, y0 + ty * w * sx, -0.003 - h * sz)) for sx, sz in
              ((-1, 0), (1, 0), (1, 1), (-1, 1))]
        bm.faces.new(vs)
    me = bpy.data.meshes.get("GLISS_BASE_DETAILS") or bpy.data.meshes.new("GLISS_BASE_DETAILS")
    bm.to_mesh(me)
    bm.free()
    det = _part("GLISS_BASE_DETAILS", me, mount, bpy.data.materials.get("MAT_BLACK_RECESS") or blk)
    det.visible_shadow = False
    # write back to the root
    root["dimension_register_json"] = json.dumps(reg, indent=1)
    root["pivot_depth_m"] = -zp
    root["emitter_head_local_m"] = (0.0, -R, zc)
    root["housing_radius_m"] = R
    root["validation_status"] = "PROVISIONAL_UNTIL_MEASURED"
    for k, v in reg["dimensions_mm"].items():
        root["dim_%s_mm" % k] = v["value"]
        root["dim_%s_status" % k] = v["status"]
    return reg


def aim_fixture(mount_ob, head_ob, target, iterations=4):
    """Pan the mount about Z and tilt the head about X so the optical axis through the emitter hits `target`."""
    root = bpy.data.objects["GLISS_MASTER_ROOT"]
    piv = Vector((0, 0, -root["pivot_depth_m"]))
    em = Vector(root["emitter_head_local_m"])
    mloc = mount_ob.location.copy()
    pan, tilt = 0.0, 0.0
    for _ in range(iterations):
        Rz = Matrix.Rotation(pan, 3, "Z")
        Rx = Matrix.Rotation(tilt, 3, "X")
        emw = mloc + Rz @ (piv + Rx @ em)
        dvec = (Vector(target) - emw).normalized()
        tilt = math.acos(max(-1.0, min(1.0, -dvec.z)))
        pan = math.atan2(-dvec.x, dvec.y)
    mount_ob.rotation_euler = (0, 0, pan)
    head_ob.location = piv
    head_ob.rotation_euler = (tilt, 0, 0)
    return pan, tilt
