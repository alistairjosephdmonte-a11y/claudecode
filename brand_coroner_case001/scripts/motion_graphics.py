"""Motion-graphics toolkit: editable typography, evidence cards, data bars, connecting lines, source tags.
A Stage maps 2D layout coordinates (u right, v up, metres) onto either a front-facing plane ('front', graphics stages)
or a tabletop ('flat', archive light table). All values shown on screen come from config.EVIDENCE status."""
import math

import bpy
from mathutils import Vector

import assets as A
import config as C


class Stage:
    def __init__(self, name, coll_, origin, kind, M, f0, f1, table_z=0.0):
        self.name, self.c, self.o, self.kind, self.M, self.f0, self.f1 = name, coll_, Vector(origin), kind, M, f0, f1
        self.table_z = table_z
        self.n = 0

    # coordinate mapping
    def p(self, u, v, d=0.0):
        if self.kind == "front":
            return self.o + Vector((u, -d, v))
        return self.o + Vector((u, v, self.table_z + d))

    def rot(self, deg=0.0):
        if self.kind == "front":
            return (math.radians(90), 0, math.radians(deg) * 0)
        return (0, 0, math.radians(deg))

    def _nm(self, base):
        self.n += 1
        return f"{self.name}_{base}_{self.n:02d}"

    # primitives
    def backdrop(self, w=34.0, h=19.5, grid=True):
        A.box(self._nm("Backdrop"), self.c, tuple(self.p(0, 0, -0.6)), (w, 0.05, h) if self.kind == "front" else (w, h, 0.02), self.M["black"])
        if grid:
            g = A.mat_basic("MAT_Grid_Line", tuple(x * 0.35 for x in A.pal("ARCHIVE_GREY")), 0.9)
            for i in range(-8, 9, 2):
                A.box(self._nm("GridV"), self.c, tuple(self.p(i, 0, -0.55)), (0.006, 0.01, h) if self.kind == "front" else (0.006, h, 0.002), g)
            for j in range(-4, 5, 2):
                A.box(self._nm("GridH"), self.c, tuple(self.p(0, j, -0.55)), (w, 0.01, 0.006) if self.kind == "front" else (w, 0.006, 0.002), g)

    def card(self, base, u, v, w, h, mat, d=0.0, thick=0.012, deg=0.0, bevel=0.0):
        size = (w, thick, h) if self.kind == "front" else (w, h, thick)
        rot = (0, math.radians(deg), 0) if self.kind == "front" else (0, 0, math.radians(deg))
        return A.box(self._nm(base), self.c, tuple(self.p(u, v, d + thick / 2)), size, mat, rot=rot, bevel=bevel)

    def text(self, base, body, u, v, size, color="EVIDENCE_IVORY", kind="regular", align="LEFT", d=0.02, fade=None,
             deg=0.0, width=None, mat=None):
        m = mat or A.mat_fade(f"MAT_TXT_{self.name}_{self.n + 1:02d}", A.pal(color) if isinstance(color, str) else color, 0.6)
        rot = (math.radians(90), 0, 0) if self.kind == "front" else (0, 0, math.radians(deg))
        t = A.text(self._nm(base), body, self.c, tuple(self.p(u, v, d)), size, m, kind, align, rot, width=width)
        if fade and mat is None:
            A.key_fade(m, [(self.f0, 0.0), (fade[0], 0.0), (fade[1], 1.0)] + ([(fade[2], 1.0), (fade[3], 0.0)] if len(fade) == 4 else []))
        return t

    def bar(self, base, u, v, w, h, mat, grow=None, d=0.0, depth=0.3, direction="up"):
        """A data bar anchored at its base; grow=(f_start, f_end) animates its length (controlled chart growth)."""
        nm = self._nm(base)
        if direction == "up":
            boxes = [((0, 0, h / 2), (w, depth, h), mat)] if self.kind == "front" else [((0, h / 2, 0), (w, h, depth), mat)]
        elif direction == "down":
            boxes = [((0, 0, -h / 2), (w, depth, h), mat)]
        else:
            boxes = [((w / 2, 0, 0), (w, depth, h), mat)] if self.kind == "front" else [((w / 2, 0, 0), (w, h, depth), mat)]
        o = A.obj(nm, A.mesh_boxes(nm, boxes), self.c, tuple(self.p(u, v, d + depth / 2)))
        if grow:
            axis = 2 if direction in ("up", "down") and self.kind == "front" else (1 if direction == "up" else 0)
            sc = [1.0, 1.0, 1.0]
            for f, k in ((self.f0, 0.001), (grow[0], 0.001), (grow[1], 1.0)):
                sc[axis] = k
                o.scale = sc
                o.keyframe_insert("scale", frame=f)
        return o

    def line(self, base, u0, v0, u1, v1, mat, thick=0.03, grow=None, d=0.01):
        a, b = Vector((u0, v0)), Vector((u1, v1))
        ln = (b - a).length
        ang = math.atan2(b.y - a.y, b.x - a.x)
        nm = self._nm(base)
        if self.kind == "front":
            o = A.obj(nm, A.mesh_boxes(nm, [((ln / 2, 0, 0), (ln, thick, thick), mat)]), self.c, tuple(self.p(u0, v0, d)), (0, -ang, 0))
        else:
            o = A.obj(nm, A.mesh_boxes(nm, [((ln / 2, 0, 0), (ln, thick, 0.002), mat)]), self.c, tuple(self.p(u0, v0, d)), (0, 0, ang))
        if grow:
            for f, k in ((self.f0, 0.001), (grow[0], 0.001), (grow[1], 1.0)):
                o.scale = (k, 1, 1)
                o.keyframe_insert("scale", frame=f)
        return o

    def ring(self, base, u, v, r_in, r_out, mat, d=0.02, seg=64):
        nm = self._nm(base)
        verts, faces = [], []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            for r in (r_in, r_out):
                if self.kind == "front":
                    verts.append((r * math.cos(a), 0, r * math.sin(a)))
                else:
                    verts.append((r * math.cos(a), r * math.sin(a), 0))
        for j in range(seg):
            k = (j + 1) % seg
            faces.append((2 * j, 2 * k, 2 * k + 1, 2 * j + 1))
        me = bpy.data.meshes.new(nm)
        me.from_pydata(verts, [], faces)
        me.materials.append(mat)
        return A.obj(nm, me, self.c, tuple(self.p(u, v, d)))

    def dots(self, base, pts, r, mat, build=None, d=0.02, order_from=(0.0, 0.0), reverse=False):
        """Many markers in one mesh; a Build modifier reveals them over (start, length) frames, nearest-first."""
        nm = self._nm(base)
        pts = sorted(pts, key=lambda q: (q[0] - order_from[0]) ** 2 + (q[1] - order_from[1]) ** 2)
        boxes = [(tuple(self.p(u, v, d) - self.o), (r, r, r), mat) for u, v in pts]
        o = A.obj(nm, A.mesh_boxes(nm, boxes), self.c, tuple(self.o))
        if build:
            b = o.modifiers.new("Build", "BUILD")
            b.frame_start, b.frame_duration = build
            b.use_reverse = reverse
        return o

    def source_tag(self, src_id, u, v, size=0.16, align="LEFT", d=0.02):
        """Source attribution that cannot drift from the register: VERIFIED (grey) or PENDING (Verdict Red)."""
        e = C.EVIDENCE_BY_ID[src_id]
        verified = e["status"].startswith("verified")
        label = f"{src_id}  ·  {'VERIFIED SOURCE' if verified else 'PENDING VERIFICATION'}"
        return self.text("SourceTag", label, u, v, size, "ARCHIVE_GREY" if verified else "VERDICT_RED", "semibold", align, d)

    def slide_in(self, o, du, dv, fa, fb):
        end = o.location.copy()
        start = end + (Vector((du, 0, dv)) if self.kind == "front" else Vector((du, dv, 0)))
        for f, p in ((self.f0, start), (fa, start), (fb, end)):
            o.location = p
            o.keyframe_insert("location", frame=f)
        from camera_rigs import _ease
        _ease(o)
        return o


def is_verified(src_id):
    return C.EVIDENCE_BY_ID[src_id]["status"].startswith("verified")
