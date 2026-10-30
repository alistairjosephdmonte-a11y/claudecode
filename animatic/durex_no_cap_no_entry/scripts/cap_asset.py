"""Reusable six-panel baseball cap asset. Every cap in the film links this ONE mesh datablock."""
import math
from math import sin, cos, pi, radians
import bpy
import bmesh
from mathutils import Vector, Matrix

from common import (CAP_BLUE_PLACEHOLDER, cap_twill, principled, mesh_from_bm, new_object, srgb)

CAP_MESH_NAME = "ASSET_HERO_CAP_MESH"
RX, RY, H = 0.088, 0.100, 0.105  # crown base half-width, half-depth, crown height (metres)
SLOT_TWILL, SLOT_THREAD, SLOT_BUTTON, SLOT_BUCKLE, SLOT_INNER, SLOT_SPARE = range(6)

PANEL_OFFS = [0, 1.2, 2.4, 7, 12, 18, 24, 30, 36, 42, 48, 53, 57.6, 58.8]
ROWS = [0.0, 0.04, 0.1, 0.18, 0.27, 0.37, 0.47, 0.57, 0.66, 0.74, 0.81, 0.87, 0.92, 0.96]


def crown_point(az_deg, v, inset=0.0):
    phi = v * pi / 2
    a = radians(az_deg)
    rho = cos(phi) ** 0.92
    k = 1.0 - inset
    return Vector((RX * cos(a) * rho * k, RY * sin(a) * rho * k, H * sin(phi)))


def build_cap_mesh():
    me = bpy.data.meshes.get(CAP_MESH_NAME)
    if me:
        return me
    bm = bmesh.new()
    st = bm.verts.layers.float.new("stitch")

    # --- crown: six panels, seam grooves at front-centre and every 60 deg
    azs, groove, stitch_col = [], [], []
    for k in range(6):
        s = -90 + 60 * k
        for o in PANEL_OFFS:
            azs.append(s + o)
            groove.append(o == 0)
            stitch_col.append(o in (1.2, 58.8))
    ncol = len(azs)
    grid = []
    for ri, v in enumerate(ROWS):
        row = []
        for ci, az in enumerate(azs):
            inset = 0.028 if (groove[ci] and 0.0 < v < 0.97) else 0.0
            vert = bm.verts.new(crown_point(az, v, inset))
            vert[st] = 1.0 if ((stitch_col[ci] and v > 0.02) or ri == 1) else 0.0
            row.append(vert)
        grid.append(row)
    top = bm.verts.new((0, 0, H))
    top[st] = 0.0
    crown_faces = []
    for r in range(len(ROWS) - 1):
        for c in range(ncol):
            c2 = (c + 1) % ncol
            crown_faces.append(bm.faces.new((grid[r][c], grid[r][c2], grid[r + 1][c2], grid[r + 1][c])))
    for c in range(ncol):
        crown_faces.append(bm.faces.new((grid[-1][c], grid[-1][(c + 1) % ncol], top)))
    bmesh.ops.recalc_face_normals(bm, faces=crown_faces)
    for f in crown_faces:
        if f.normal.dot(f.calc_center_median()) < 0:
            f.normal_flip()
        f.material_index = SLOT_TWILL
    bmesh.ops.solidify(bm, geom=crown_faces, thickness=0.0022)

    # --- curved brim (D-shape, curved down across its width, slight downward pitch)
    t_rows = [0.0, 0.3, 0.55, 0.72, 0.8, 0.87, 0.94, 1.0]
    t_stitch = {0.8, 0.87, 0.94}
    M = 28
    th0, th1 = -90 - 78, -90 + 78
    bgrid = []
    for i in range(M + 1):
        t = i / M
        th = radians(lerp_(th0, th1, t))
        p_in = Vector((RX * 0.985 * cos(th), RY * 0.985 * sin(th), 0.002))
        n = Vector((cos(th) / RX, sin(th) / RY, 0)).normalized()
        w = 0.074 * (sin(pi * t) ** 0.55) + 0.003
        row = []
        for r in t_rows:
            p = p_in + n * (w * r)
            p.z -= 0.016 * (p.x / 0.095) ** 2 * r + 0.16 * w * r
            vert = bm.verts.new(p)
            vert[st] = 1.0 if r in t_stitch and 0.08 < t < 0.92 else 0.0
            row.append(vert)
        bgrid.append(row)
    brim_faces = []
    for i in range(M):
        for j in range(len(t_rows) - 1):
            f = bm.faces.new((bgrid[i][j], bgrid[i + 1][j], bgrid[i + 1][j + 1], bgrid[i][j + 1]))
            f.material_index = SLOT_TWILL
            brim_faces.append(f)
    for f in brim_faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    bmesh.ops.solidify(bm, geom=brim_faces, thickness=0.0038)

    # --- top button
    r = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * 0.0095, v.co.y * 0.0095, v.co.z * 0.0045 + H + 0.0005))
    _assign(bm, r["verts"], SLOT_BUTTON)

    # --- six embroidered eyelets, one per panel
    for k in range(6):
        az = -90 + 60 * k + 30
        p = crown_point(az, 0.62)
        nrm = Vector((p.x / RX ** 2, p.y / RY ** 2, p.z / H ** 2)).normalized()
        vs = _torus(bm, p + nrm * 0.0006, nrm, 0.0034, 0.0011)
        _assign(bm, vs, SLOT_THREAD)

    # --- rear arch opening (dark) + adjustment strap + buckle
    arch = []
    A, B = 9, 5
    for i in range(A + 1):
        a = -1 + 2 * i / A
        row = []
        for j in range(B + 1):
            b = j / B
            z = 0.021 + b * 0.034 * math.sqrt(max(0.0, 1 - a * a))
            phi = math.asin(min(0.99, z / H))
            az = radians(90 + 17 * a)
            rho = cos(phi) ** 0.92 * 1.007
            row.append(bm.verts.new((RX * cos(az) * rho, RY * sin(az) * rho, z)))
        arch.append(row)
    for i in range(A):
        for j in range(B):
            f = bm.faces.new((arch[i][j], arch[i + 1][j], arch[i + 1][j + 1], arch[i][j + 1]))
            f.material_index = SLOT_INNER
    strap = []
    S = 12
    for i in range(S + 1):
        az = radians(90 - 26 + 52 * i / S)
        row = [bm.verts.new((RX * cos(az) * 1.018, RY * sin(az) * 1.018, z)) for z in (0.004, 0.021)]
        strap.append(row)
    strap_faces = []
    for i in range(S):
        f = bm.faces.new((strap[i][0], strap[i + 1][0], strap[i + 1][1], strap[i][1]))
        f.material_index = SLOT_TWILL
        strap_faces.append(f)
    for f in strap_faces:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() * Vector((1, 1, 0))) < 0:
            f.normal_flip()
    bmesh.ops.solidify(bm, geom=strap_faces, thickness=0.0018)
    az = radians(100)
    c = Vector((RX * cos(az) * 1.04, RY * sin(az) * 1.04, 0.0125))
    rb = bmesh.ops.create_cube(bm, size=1.0)
    rot = Matrix.Rotation(az + pi / 2, 3, "Z")
    for v in rb["verts"]:
        v.co = rot @ Vector((v.co.x * 0.016, v.co.y * 0.004, v.co.z * 0.019)) + c
    _assign(bm, rb["verts"], SLOT_BUCKLE)

    me = mesh_from_bm(CAP_MESH_NAME, bm)
    twill = cap_twill("MAT_CAP_TWILL_HERO_BLUE", CAP_BLUE_PLACEHOLDER)
    thread = principled("MAT_CAP_THREAD_HERO_BLUE", _shade(CAP_BLUE_PLACEHOLDER, 0.55), rough=0.8, sheen=0.3)
    buckle = principled("MAT_CAP_BUCKLE", "#3E4044", rough=0.5, metal=0.8)
    inner = principled("MAT_CAP_INNER_DARK", "#0B0D14", rough=0.95)
    for m in (twill, thread, twill, buckle, inner, twill):
        me.materials.append(m)
    me["asset"] = "HERO_CAP_v01"
    me["note"] = "Single shared mesh: every cap object links this datablock (identical topology)."
    return me


def lerp_(a, b, t):
    return a + (b - a) * t


def _shade(hexcol, k):
    c = srgb(hexcol)
    to = lambda x: max(0, min(255, int(round(((1.055 * (x ** (1 / 2.4)) - 0.055) if x > 0.0031308 else x * 12.92) * 255))))
    return "#%02X%02X%02X" % tuple(to(ch * k) for ch in c[:3])


def _assign(bm, verts, slot):
    vs = set(verts)
    for f in bm.faces:
        if all(v in vs for v in f.verts):
            f.material_index = slot


def _torus(bm, center, axis, R, r, M=14, N=6):
    q = Vector((0, 0, 1)).rotation_difference(axis).to_matrix()
    rings = []
    for i in range(M):
        u = 2 * pi * i / M
        ring = []
        for j in range(N):
            w = 2 * pi * j / N
            p = Vector(((R + r * cos(w)) * cos(u), (R + r * cos(w)) * sin(u), r * sin(w)))
            ring.append(bm.verts.new(q @ p + center))
        rings.append(ring)
    for i in range(M):
        for j in range(N):
            bm.faces.new((rings[i][j], rings[(i + 1) % M][j], rings[(i + 1) % M][(j + 1) % N], rings[i][(j + 1) % N]))
    return [v for ring in rings for v in ring]


def cap_object(name, coll, override=None, scale=1.0):
    """Create an object linking the shared cap mesh. `override` maps slot index -> material (object-level)."""
    me = build_cap_mesh()
    ob = new_object(name, me, coll)
    ob.scale = (scale, scale, scale)
    if override:
        for i, slot in enumerate(ob.material_slots):
            slot.link = "OBJECT"
            slot.material = override.get(i, me.materials[i])
    ob["cap_asset"] = "HERO_CAP_v01"
    return ob
