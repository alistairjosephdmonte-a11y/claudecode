"""2D editorial motion-design toolkit for Blender (orthographic, flat Workbench shading, exact brand colours).
World units: an orthographic scale of 16 frames 16 x 9 units, so 1 unit = 120 px at 1920x1080. Time in seconds is local
to each 30 s scene (frame = 1 + round(t * 24))."""
import json
import math
import os

import bmesh
import bpy

import config as C

CROPS = json.load(open(os.path.join(C.P["meta"], "document_crops.json")))
_FONTS = {}


def lin(hexstr):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def col(name):
    return lin(C.PALETTE.get(name, name))


def font(k):
    if k not in _FONTS:
        _FONTS[k] = bpy.data.fonts.load(C.FONTS[k], check_existing=True)
    return _FONTS[k]


def F(t):
    return 1 + int(round(t * C.FPS))


def fcurves(idb):
    from bpy_extras import anim_utils
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    return cb.fcurves if cb else []


class Scene:
    def __init__(self, n):
        self.n = n
        self.name = f"SC{n:02d}"
        sc = bpy.data.scenes.new(self.name)
        self.sc = sc
        sc.frame_start, sc.frame_end = 1, C.SCENE_FRAMES
        sc.render.fps = C.FPS
        sc.render.resolution_x, sc.render.resolution_y = C.RES
        sc.render.resolution_percentage = 100
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.display_settings.display_device = "sRGB"
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light, sh.color_type = "FLAT", "TEXTURE"
        sh.show_shadows = sh.show_cavity = sh.show_object_outline = False
        sc.display.render_aa = "8"
        w = bpy.data.worlds.new(f"W_{self.name}")
        w.color = col("bg")
        sc.world = w
        cd = bpy.data.cameras.new(f"CAM_{self.name}")
        cd.type, cd.ortho_scale, cd.clip_start, cd.clip_end = "ORTHO", 16, 0.1, 200
        self.cam = bpy.data.objects.new(f"CAM_{self.name}", cd)
        sc.collection.objects.link(self.cam)
        self.cam.location = (0, 0, 60)
        sc.camera = self.cam
        self.z = 0.0
        # HUD: follows the camera and scales with the orthographic zoom (driver, simple expression: no scripts needed)
        self.hud = bpy.data.objects.new(f"HUD_{self.name}", None)
        sc.collection.objects.link(self.hud)
        self.hud.parent = self.cam
        self.hud.location = (0, 0, -10)
        for i in range(3):
            d = self.hud.driver_add("scale", i).driver
            d.type = "SCRIPTED"
            v = d.variables.new()
            v.name, v.type = "s", "SINGLE_PROP"
            v.targets[0].id_type, v.targets[0].id, v.targets[0].data_path = "CAMERA", cd, "ortho_scale"
            d.expression = "s/16"
        self.log = {"scene": self.name, "objects": 0, "highlights": [], "placeholders": [], "docs": []}
        self.veil = self.rect(0, 0, 60, 40, "bg", 0.0, parent=self.hud, zl=1.0, name="VEIL")

    # ---------------------------------------------------------------- primitives
    def _z(self, z):
        if z is not None:
            return z
        self.z += 0.002
        return self.z

    def _link(self, name, data, x, y, z, parent=None):
        o = bpy.data.objects.new(f"{self.name}_{name}", data)
        self.sc.collection.objects.link(o)
        o.location = (x, y, z)
        if parent:
            o.parent = parent
        self.log["objects"] += 1
        return o

    def _mat(self, o, color, alpha, image=None):
        m = bpy.data.materials.new(f"M_{o.name}")
        m.diffuse_color = (*col(color), alpha)
        if image:
            m.use_nodes = True
            tx = m.node_tree.nodes.new("ShaderNodeTexImage")
            tx.image = bpy.data.images.load(image, check_existing=True)
            tx.interpolation = "Cubic"
            m.node_tree.nodes.active = tx
        o.data.materials.append(m)
        o["a"] = alpha
        return m

    def _mesh(self, name, verts, faces, uvs=None):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        if uvs:
            uv = me.uv_layers.new()
            for loop in me.loops:
                uv.data[loop.index].uv = uvs[loop.vertex_index]
        return me

    def rect(self, x, y, w, h, color="type", alpha=1.0, anchor="c", z=None, parent=None, zl=None, name="rect", image=None, uv=None):
        ox = {"c": -w / 2, "l": 0, "r": -w, "b": -w / 2, "t": -w / 2}[anchor]
        oy = {"c": -h / 2, "l": -h / 2, "r": -h / 2, "b": 0, "t": -h}[anchor]
        v = [(ox, oy, 0), (ox + w, oy, 0), (ox + w, oy + h, 0), (ox, oy + h, 0)]
        u0, v0, u1, v1 = uv or (0, 0, 1, 1)
        me = self._mesh(name, v, [(0, 1, 2, 3)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
        o = self._link(name, me, x, y, zl if zl is not None else self._z(z), parent)
        self._mat(o, color, alpha, image)
        return o

    def disc(self, x, y, r, color="red", alpha=1.0, z=None, name="disc", inner=0.0, seg=64):
        bm = bmesh.new()
        if inner <= 0:
            bmesh.ops.create_circle(bm, cap_ends=True, segments=seg, radius=r)
        else:
            outer = [bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0)) for a in (2 * math.pi * i / seg for i in range(seg))]
            inn = [bm.verts.new((math.cos(a) * inner, math.sin(a) * inner, 0)) for a in (2 * math.pi * i / seg for i in range(seg))]
            for i in range(seg):
                j = (i + 1) % seg
                bm.faces.new((outer[i], outer[j], inn[j], inn[i]))
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        o = self._link(name, me, x, y, self._z(z))
        self._mat(o, color, alpha)
        return o

    def ring(self, x, y, r, th=0.045, color="type", alpha=1.0, z=None, name="ring"):
        return self.disc(x, y, r, color, alpha, z, name, inner=r - th)

    def tri(self, x, y, size, angle, color="red", alpha=1.0, z=None, name="tri"):
        me = self._mesh(name, [(size, 0, 0), (-size * 0.6, size * 0.6, 0), (-size * 0.6, -size * 0.6, 0)], [(0, 1, 2)])
        o = self._link(name, me, x, y, self._z(z))
        o.rotation_euler.z = angle
        self._mat(o, color, alpha)
        return o

    def text(self, body, x, y, size=0.3, color="type", fnt="semi", align="LEFT", alpha=1.0, z=None, width=None, parent=None,
             zl=None, valign="CENTER", spacing=1.0, line=1.0, name="txt"):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = body
        cu.font = font(fnt)
        cu.size = size
        cu.align_x = align
        cu.align_y = valign
        cu.space_character = spacing
        cu.space_line = line
        if width:
            cu.text_boxes[0].width = width
            cu.text_boxes[0].x = {"LEFT": 0, "CENTER": -width / 2, "RIGHT": -width}[align]
        o = self._link(name, cu, x, y, zl if zl is not None else self._z(None), parent)
        self._mat(o, color, alpha)
        return o

    # ---------------------------------------------------------------- animation
    def alpha(self, o, keys):
        m = o.active_material
        for t, a in keys:
            m.diffuse_color[3] = a
            m.keyframe_insert("diffuse_color", index=3, frame=F(t))

    def life(self, objs, t_in, t_out=None, d=0.5, d_out=None):
        for o in objs if isinstance(objs, (list, tuple)) else [objs]:
            a = o.get("a", 1.0)
            lag = d if o.get("overlay") else 0.0       # overlays wait for their opaque base (no transparent-on-transparent)
            k = [(t_in + lag, 0.0), (t_in + lag + d, a)]
            if t_out is not None:
                k += [(t_out - (d_out or d) - lag, a), (t_out - lag, 0.0)]
            self.alpha(o, k)
        return objs

    def dim(self, objs, t, to=0.18, d=0.8):
        for o in objs if isinstance(objs, (list, tuple)) else [objs]:
            a = o.get("a", 1.0)
            self.alpha(o, [(t, a), (t + d, to * a)])

    def move(self, o, keys, linear=False):
        for t, p in keys:
            o.location.x, o.location.y = p[0], p[1]
            o.keyframe_insert("location", index=0, frame=F(t))
            o.keyframe_insert("location", index=1, frame=F(t))
        if linear:
            for fc in fcurves(o):
                for k in fc.keyframe_points:
                    k.interpolation = "LINEAR"

    def scale(self, o, keys, axes=(0,)):
        for t, s in keys:
            for i in axes:
                o.scale[i] = max(s, 1e-4)
                o.keyframe_insert("scale", index=i, frame=F(t))

    def grow(self, o, t0, t1, axes=(0,)):
        self.scale(o, [(t0, 0.0), (t1, 1.0)], axes)
        return o

    def line(self, x, y, length, t0, t1, th=0.03, color="red", alpha=1.0, angle=0.0, z=None, name="line"):
        o = self.rect(x, y, length, th, color, alpha, anchor="l", z=z, name=name)
        o.rotation_euler.z = angle
        self.grow(o, t0, t1)
        return o

    def vline(self, x, y, length, t0, t1, th=0.025, color="rule", alpha=1.0, name="vline"):
        o = self.rect(x, y, th, length, color, alpha, anchor="b", name=name)
        self.grow(o, t0, t1, axes=(1,))
        return o

    def flow(self, x0, y0, x1, y1, t0, t1, color="red", n=6, period=2.4, r=0.06):
        dots = []
        for i in range(n):
            d = self.disc(x0, y0, r, color, 1.0, name="flow")
            ph = period * i / n
            self.move(d, [(t0 - period + ph, (x0, y0)), (t0 + ph, (x1, y1))], linear=True)
            for fc in fcurves(d):
                fc.modifiers.new("CYCLES")
            self.life(d, t0, t1, d=0.4)
            dots.append(d)
        return dots

    def group(self, x, y, name="grp"):
        e = bpy.data.objects.new(f"{self.name}_{name}", None)
        self.sc.collection.objects.link(e)
        e.location = (x, y, 0)
        return e

    def parent(self, objs, e):
        for o in objs:                               # groups are never rotated or scaled at build time
            o.parent = e
            o.location.x -= e.location.x
            o.location.y -= e.location.y

    # ---------------------------------------------------------------- camera
    def shots(self, segs):
        """segs: list of shots; each shot is a list of (t, x, y, ortho_scale) keys eased in between. Between shots: a cut."""
        cam, cd = self.cam, self.cam.data
        for si, seg in enumerate(segs):
            for ki, (t, x, y, s) in enumerate(seg):
                f = F(t)
                if ki == len(seg) - 1 and si < len(segs) - 1:
                    f = F(segs[si + 1][0][0]) - 1          # hold to the frame before the next shot, then cut
                cam.location.x, cam.location.y, cd.ortho_scale = x, y, s
                cam.keyframe_insert("location", index=0, frame=f)
                cam.keyframe_insert("location", index=1, frame=f)
                cd.keyframe_insert("ortho_scale", frame=f)
        cuts = {F(seg[0][0]) - 1 for seg in segs[1:]}
        for idb in (cam, cd):
            for fc in fcurves(idb):
                for k in fc.keyframe_points:
                    k.interpolation = "CONSTANT" if int(round(k.co.x)) in cuts else "BEZIER"
                    k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
                fc.update()
        self.log["shots"] = [[list(k) for k in seg] for seg in segs]

    def fade_black(self, t0, t1, a0, a1):
        self.alpha(self.veil, [(t0, a0), (t1, a1)])

    # ---------------------------------------------------------------- editorial elements
    def hud_text(self, body, x, y, size, color, fnt="semi", align="LEFT", alpha=1.0, width=None):
        return self.text(body, x, y, size, color, fnt, align, alpha, parent=self.hud, zl=0.5, width=width, name="hud")

    def header(self, act, title):
        a = self.hud_text("brand coroner · case 002 · wework", -7.35, 4.08, 0.16, "gray", alpha=0.9)
        b = self.hud_text(act, 7.35, 4.08, 0.16, "gray", align="RIGHT", alpha=0.9)
        c = self.hud_text(f"{self.n:02d} · {title}", -7.35, 3.74, 0.2, "type", fnt="bold")
        self.life([a, b], 0.3, 29.7, d=0.6)
        self.life(c, 0.5, 5.0, d=0.6, d_out=0.8)

    def source(self, ids, t0, t1):
        objs = []
        for i, sid in enumerate(ids[::-1]):
            s = C.SOURCES[sid]
            y = -4.12 + i * 0.27
            tag = {"verified": ("source", "gray"), "reported": ("reported", "red"), "illustrative": ("illustrative", "red")}[s["status"]]
            objs.append(self.hud_text(tag[0], -7.35, y, 0.16, tag[1], fnt="bold"))
            objs.append(self.hud_text(s["label"], -6.15, y, 0.16, "type", alpha=0.85))
        self.life(objs, t0 + 0.4, t1 - 0.15, d=0.4, d_out=0.3)
        return objs

    def doc(self, cid, x, y, w, crop_top=0, crop_bottom=0, border=True):
        meta = CROPS[cid]
        cw, ch = meta["css_w"], meta["css_h"]
        vis = ch - crop_top - crop_bottom
        h = w * vis / cw
        img = os.path.join(C.ROOT, meta["png"])
        objs = []
        if border:      # four strips, never underneath the page: overlapping transparent layers average in Workbench
            e = 0.03
            for (bx, by, bw, bh) in ((x, y + h / 2 + e / 2, w + 2 * e, e), (x, y - h / 2 - e / 2, w + 2 * e, e),
                                     (x - w / 2 - e / 2, y, e, h), (x + w / 2 + e / 2, y, e, h)):
                objs.append(self.rect(bx, by, bw, bh, "rule", 1.0, name=f"{cid}_edge"))
        uv = (0, crop_bottom / ch, 1, 1 - crop_top / ch)
        p = self.rect(x, y, w, h, "#FFFFFF", 1.0, name=cid, image=img, uv=uv)
        objs.append(p)
        self.log["docs"].append(cid)
        return Doc(self, cid, x, y, w, h, cw, crop_top, objs)

    def placeholder(self, pid, x, y, w, h):
        title, need = C.PLACEHOLDERS[pid]
        o = [self.rect(x, y, w, h, "panel", 1.0, name=f"{pid}_panel")]
        th = 0.022
        for (cx, cy, ww, hh) in ((x, y + h / 2, w, th), (x, y - h / 2, w, th), (x - w / 2, y, th, h), (x + w / 2, y, th, h)):
            o.append(self.rect(cx, cy, ww, hh, "rule", 1.0, name="pborder"))
        # crop marks in the brand red, so the slot reads as an unfilled frame, never as an image
        L = min(w, h) * 0.08
        for sx in (-1, 1):
            for sy in (-1, 1):
                o.append(self.rect(x + sx * (w / 2 - L / 2), y + sy * h / 2, L, 0.03, "red", 1.0, name="pmark"))
                o.append(self.rect(x + sx * w / 2, y + sy * (h / 2 - L / 2), 0.03, L, "red", 1.0, name="pmark"))
        pad = 0.28
        tw = w - 2 * pad
        sz = min(0.2, max(0.13, w * 0.032))
        o.append(self.text(f"placeholder · {pid}", x - w / 2 + pad, y + h / 2 - pad, sz * 0.8, "red", "bold", valign="TOP"))
        o.append(self.text(title, x - w / 2 + pad, y + h / 2 - pad - sz * 1.4, sz * 1.25, "type", "bold", width=tw, valign="TOP"))
        o.append(self.text(f"asset required: {need}", x - w / 2 + pad, y - h / 2 + pad, sz * 0.8, "gray", "regular", width=tw,
                           valign="BOTTOM", line=1.1))
        o.append(self.text("no generated or simulated imagery", x + w / 2 - pad, y + h / 2 - pad, sz * 0.7, "gray", "semi",
                           align="RIGHT", valign="TOP"))
        for ob in o[1:]:
            ob["overlay"] = True
        self.log["placeholders"].append(pid)
        return o


class Doc:
    """An authentic document crop placed in the scene; maps the recorded pixel rectangles of phrases to world space."""

    def __init__(self, S, cid, x, y, w, h, css_w, crop_top, objs):
        self.S, self.cid, self.x, self.y, self.w, self.h = S, cid, x, y, w, h
        self.k = w / css_w
        self.top = crop_top
        self.objs = objs
        self.marks = {m["text"]: m["rects"] for m in CROPS[cid]["marks"]}

    def rects(self, mark):
        out = []
        for r in self.marks.get(mark, []):
            cx = self.x - self.w / 2 + (r["x"] + r["w"] / 2) * self.k
            cy = self.y + self.h / 2 - (r["y"] - self.top + r["h"] / 2) * self.k
            out.append((cx, cy, r["w"] * self.k, r["h"] * self.k))
        if not out:
            raise KeyError(f"{self.cid}: phrase not captured: {mark}")
        return out

    def center(self, mark):
        rs = self.rects(mark)
        xs = [r[0] - r[2] / 2 for r in rs] + [r[0] + r[2] / 2 for r in rs]
        ys = [r[1] - r[3] / 2 for r in rs] + [r[1] + r[3] / 2 for r in rs]
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys)

    def highlight(self, mark, t, t_out=None, fill=0.22, underline=True, color="red", pad=0.03):
        """Forensic highlight: translucent box fades in, then a red underline draws left to right."""
        S, objs = self.S, []
        for i, (cx, cy, w, h) in enumerate(self.rects(mark)):
            b = S.rect(cx, cy, w + 2 * pad, h + 2 * pad, color, fill, name="hl_box")
            S.life(b, t + i * 0.15, t_out, d=0.35)
            objs.append(b)
            if underline:
                u = S.rect(cx - w / 2 - pad, cy - h / 2 - pad, w + 2 * pad, max(0.022, h * 0.09), color, 1.0, anchor="l", name="hl_line")
                S.grow(u, t + 0.2 + i * 0.15, t + 0.75 + i * 0.15)
                if t_out is not None:
                    S.life(u, t + 0.2, t_out, d=0.05)
                objs.append(u)
        S.log["highlights"].append({"doc": self.cid, "phrase": mark, "t": t})
        return objs

    def focus(self, mark, t, t_out=None, a=0.62):
        """Dims the document around a phrase (four masks inside the document bounds)."""
        S = self.S
        cx, cy, w, h = self.center(mark)
        p = 0.08
        L, R, B, T = self.x - self.w / 2, self.x + self.w / 2, self.y - self.h / 2, self.y + self.h / 2
        x0, x1, y0, y1 = cx - w / 2 - p, cx + w / 2 + p, cy - h / 2 - p, cy + h / 2 + p
        boxes = [((L + R) / 2, (y1 + T) / 2, R - L, T - y1), ((L + R) / 2, (B + y0) / 2, R - L, y0 - B),
                 ((L + x0) / 2, (y0 + y1) / 2, x0 - L, y1 - y0), ((x1 + R) / 2, (y0 + y1) / 2, R - x1, y1 - y0)]
        objs = [S.rect(bx, by, bw, bh, "bg", a, name="focus") for bx, by, bw, bh in boxes if bw > 0.001 and bh > 0.001]
        S.life(objs, t, t_out, d=0.6)
        return objs
