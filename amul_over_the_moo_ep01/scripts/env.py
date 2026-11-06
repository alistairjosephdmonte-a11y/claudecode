"""Photographic environment (Cycles): sunrise sky + sun, meadow with Geometry-Nodes grass (wind + hoof flattening),
wildflowers, fences, hills, dirt path, puddle, timber barn (planked walls with light gaps, beams, hay, floor), training
block, hinged double doors, interior haze and dust. All procedural; no external textures."""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import config as C

R = random.Random(11)


def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in (parent or bpy.context.scene.collection).children:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def link(o, c):
    for u in list(o.users_collection):
        u.objects.unlink(o)
    c.objects.link(o)
    return o


def box(name, c, x0, y0, z0, x1, y1, z1, mat=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (x0 + x1) / 2 + v.co.x * (x1 - x0)
        v.co.y = (y0 + y1) / 2 + v.co.y * (y1 - y0)
        v.co.z = (z0 + z1) / 2 + v.co.z * (z1 - z0)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=2, affect="EDGES")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return nt, nt.nodes, nt.links


def N(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        if k in n.inputs:
            n.inputs[k].default_value = v
        else:
            setattr(n, k, v)
    return n


# ------------------------------------------------------------------ materials
def wood_mat(name, base=(0.32, 0.24, 0.17), grey=0.35, scale=1.0, planks=None, rough=0.72, dust=0.0):
    m = bpy.data.materials.new(name)
    nt, ns, L = nodes(m)
    out = N(nt, "ShaderNodeOutputMaterial", (900, 0))
    bs = N(nt, "ShaderNodeBsdfPrincipled", (600, 0))
    bs.inputs["Roughness"].default_value = rough
    tc = N(nt, "ShaderNodeTexCoord", (-1200, 0))
    mp = N(nt, "ShaderNodeMapping", (-1000, 0))
    mp.inputs["Scale"].default_value = (scale * 1.0, scale * 6.0, scale * 1.0) if planks == "vertical" else (scale * 6.0, scale * 1.0, scale * 1.0)
    src = tc.outputs["Object"]
    if planks == "vertical":
        sp = N(nt, "ShaderNodeSeparateXYZ", (-1350, -200))
        L.new(tc.outputs["Object"], sp.inputs[0])
        ad = N(nt, "ShaderNodeMath", (-1250, -200), operation="ADD")
        L.new(sp.outputs["X"], ad.inputs[0])
        L.new(sp.outputs["Y"], ad.inputs[1])
        cb = N(nt, "ShaderNodeCombineXYZ", (-1150, -200))
        L.new(ad.outputs[0], cb.inputs["X"])
        L.new(sp.outputs["Z"], cb.inputs["Y"])
        src = cb.outputs[0]
    L.new(src, mp.inputs["Vector"])
    wave = N(nt, "ShaderNodeTexWave", (-760, 120))
    wave.inputs["Scale"].default_value = 2.2
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 3.0
    wave.bands_direction = "Y" if planks == "vertical" else "X"
    L.new(mp.outputs["Vector"], wave.inputs["Vector"])
    noise = N(nt, "ShaderNodeTexNoise", (-760, -160))
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 8.0
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = N(nt, "ShaderNodeValToRGB", (-500, 120))
    c0 = [v * 0.55 for v in base]
    ramp.color_ramp.elements[0].color = (*c0, 1)
    ramp.color_ramp.elements[1].color = (*[min(1, v * 1.35) for v in base], 1)
    L.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    mixg = N(nt, "ShaderNodeMix", (-240, 120), data_type="RGBA")
    mixg.inputs["Factor"].default_value = grey
    mixg.inputs[7].default_value = (0.125, 0.118, 0.108, 1)    # weathered silver-grey (linear)
    L.new(ramp.outputs["Color"], mixg.inputs[6])
    col = mixg.outputs[2]
    if planks:
        br = N(nt, "ShaderNodeTexBrick", (-760, -420))
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Mortar Size"].default_value = 0.018 if planks == "vertical" else 0.012
        br.inputs["Brick Width"].default_value = 0.22 if planks == "vertical" else 1.6
        br.inputs["Row Height"].default_value = 3.0 if planks == "vertical" else 0.18
        br.offset = 0.37
        br.inputs["Color1"].default_value = (1, 1, 1, 1)
        br.inputs["Color2"].default_value = (0.72, 0.70, 0.68, 1)
        br.inputs["Mortar"].default_value = (0.05, 0.04, 0.035, 1)
        mp2 = N(nt, "ShaderNodeMapping", (-1000, -420))
        L.new(src, mp2.inputs["Vector"])
        L.new(mp2.outputs["Vector"], br.inputs["Vector"])
        mul = N(nt, "ShaderNodeMix", (0, 60), data_type="RGBA", blend_type="MULTIPLY")
        mul.inputs["Factor"].default_value = 1.0
        L.new(col, mul.inputs[6])
        L.new(br.outputs["Color"], mul.inputs[7])
        col = mul.outputs[2]
    if dust > 0:
        dm = N(nt, "ShaderNodeMix", (240, 60), data_type="RGBA")
        dn = N(nt, "ShaderNodeTexNoise", (-240, -300))
        dn.inputs["Scale"].default_value = 1.6
        dn.inputs["Detail"].default_value = 4.0
        L.new(tc.outputs["Object"], dn.inputs["Vector"])
        dr = N(nt, "ShaderNodeMapRange", (0, -300))
        dr.inputs["From Min"].default_value = 0.45
        dr.inputs["From Max"].default_value = 0.75
        dr.inputs["To Max"].default_value = dust
        L.new(dn.outputs["Fac"], dr.inputs["Value"])
        L.new(dr.outputs["Result"], dm.inputs["Factor"])
        L.new(col, dm.inputs[6])
        dm.inputs[7].default_value = (0.22, 0.19, 0.155, 1)
        col = dm.outputs[2]
    L.new(col, bs.inputs["Base Color"])
    bump = N(nt, "ShaderNodeBump", (300, -300))
    bump.inputs["Strength"].default_value = 0.25
    sc = N(nt, "ShaderNodeMath", (100, -400), operation="ADD")
    L.new(wave.outputs["Fac"], sc.inputs[0])
    L.new(noise.outputs["Fac"], sc.inputs[1])
    L.new(sc.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], bs.inputs["Normal"])
    L.new(bs.outputs[0], out.inputs[0])
    return m


def simple_mat(name, color, rough=0.8, noise_amt=0.15, scale=6.0, bump=0.2):
    m = bpy.data.materials.new(name)
    nt, ns, L = nodes(m)
    out = N(nt, "ShaderNodeOutputMaterial", (600, 0))
    bs = N(nt, "ShaderNodeBsdfPrincipled", (300, 0))
    bs.inputs["Roughness"].default_value = rough
    tc = N(nt, "ShaderNodeTexCoord", (-700, 0))
    n = N(nt, "ShaderNodeTexNoise", (-500, 0))
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 8.0
    L.new(tc.outputs["Object"], n.inputs["Vector"])
    ramp = N(nt, "ShaderNodeValToRGB", (-250, 0))
    ramp.color_ramp.elements[0].color = (*[c * (1 - noise_amt) for c in color], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + noise_amt)) for c in color], 1)
    L.new(n.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    b = N(nt, "ShaderNodeBump", (100, -250))
    b.inputs["Strength"].default_value = bump
    L.new(n.outputs["Fac"], b.inputs["Height"])
    L.new(b.outputs["Normal"], bs.inputs["Normal"])
    L.new(bs.outputs[0], out.inputs[0])
    return m


def ground_mat():
    """Ground beyond the modelled grass: pasture read from a distance (mottled greens with dry patches)."""
    m = simple_mat("M_Ground", (0.032, 0.058, 0.014), rough=0.95, noise_amt=0.55, scale=0.9, bump=0.3)
    return m


def dirt_mat(wet=0.0):
    m = simple_mat("M_Dirt" if not wet else "M_Mud", (0.17, 0.12, 0.075) if not wet else (0.10, 0.07, 0.045),
                   rough=0.9 - wet * 0.5, noise_amt=0.35, scale=14.0, bump=0.5)
    return m


def water_mat():
    m = bpy.data.materials.new("M_PuddleWater")
    nt, ns, L = nodes(m)
    out = N(nt, "ShaderNodeOutputMaterial", (600, 0))
    bs = N(nt, "ShaderNodeBsdfPrincipled", (300, 0))
    bs.inputs["Base Color"].default_value = (0.03, 0.028, 0.022, 1)
    bs.inputs["Roughness"].default_value = 0.02
    bs.inputs["IOR"].default_value = 1.33
    bs.inputs["Transmission Weight"].default_value = 0.6
    # small edge ripples: animated wave rings, strongest near the rim
    tc = N(nt, "ShaderNodeTexCoord", (-900, 0))
    wave = N(nt, "ShaderNodeTexWave", (-600, 0), wave_type="RINGS")
    wave.inputs["Scale"].default_value = 9.0
    wave.inputs["Distortion"].default_value = 1.5
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    drv = wave.inputs["Phase Offset"].driver_add("default_value").driver
    drv.expression = "frame/6"
    grad = N(nt, "ShaderNodeTexGradient", (-600, -250), gradient_type="SPHERICAL")
    mpg = N(nt, "ShaderNodeMapping", (-800, -250))
    mpg.inputs["Scale"].default_value = (1 / C.PUDDLE["rx"], 1 / C.PUDDLE["ry"], 1)
    L.new(tc.outputs["Object"], mpg.inputs["Vector"])
    L.new(mpg.outputs["Vector"], grad.inputs["Vector"])
    inv = N(nt, "ShaderNodeMath", (-400, -250), operation="SUBTRACT")
    inv.inputs[0].default_value = 1.0
    L.new(grad.outputs["Fac"], inv.inputs[1])
    mul = N(nt, "ShaderNodeMath", (-200, -100), operation="MULTIPLY")
    L.new(wave.outputs["Fac"], mul.inputs[0])
    L.new(inv.outputs[0], mul.inputs[1])
    b = N(nt, "ShaderNodeBump", (100, -200))
    b.inputs["Strength"].default_value = 0.03
    L.new(mul.outputs[0], b.inputs["Height"])
    L.new(b.outputs["Normal"], bs.inputs["Normal"])
    L.new(bs.outputs[0], out.inputs[0])
    return m


def grass_mat():
    m = bpy.data.materials.new("M_Grass")
    nt, ns, L = nodes(m)
    out = N(nt, "ShaderNodeOutputMaterial", (700, 0))
    mix = N(nt, "ShaderNodeMixShader", (500, 0))
    bs = N(nt, "ShaderNodeBsdfPrincipled", (200, 100))
    bs.inputs["Roughness"].default_value = 0.55
    tr = N(nt, "ShaderNodeBsdfTranslucent", (200, -150))
    mix.inputs[0].default_value = 0.3
    info = N(nt, "ShaderNodeObjectInfo", (-600, 0))
    ramp = N(nt, "ShaderNodeValToRGB", (-300, 0))
    ramp.color_ramp.elements[0].color = (0.022, 0.06, 0.010, 1)
    ramp.color_ramp.elements[1].color = (0.20, 0.18, 0.07, 1)
    ramp.color_ramp.elements.new(0.7).color = (0.07, 0.15, 0.025, 1)
    # per-instance variation via the geometry-nodes "variation" attribute
    att = N(nt, "ShaderNodeAttribute", (-600, -200), attribute_name="variation", attribute_type="INSTANCER")
    L.new(att.outputs["Fac"], ramp.inputs["Fac"])
    gr = N(nt, "ShaderNodeTexCoord", (-600, 250))
    sep = N(nt, "ShaderNodeSeparateXYZ", (-400, 250))
    L.new(gr.outputs["Generated"], sep.inputs[0])
    dark = N(nt, "ShaderNodeMix", (-50, 150), data_type="RGBA", blend_type="MULTIPLY")
    rr = N(nt, "ShaderNodeMapRange", (-200, 300))
    rr.inputs["To Min"].default_value = 0.35
    L.new(sep.outputs["Z"], rr.inputs["Value"])
    L.new(rr.outputs["Result"], dark.inputs["Factor"])
    L.new(ramp.outputs["Color"], dark.inputs[6])
    dark.inputs[7].default_value = (0.25, 0.25, 0.25, 1)
    L.new(dark.outputs[2], bs.inputs["Base Color"])
    L.new(dark.outputs[2], tr.inputs["Color"])
    L.new(bs.outputs[0], mix.inputs[1])
    L.new(tr.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs[0])
    return m


# ------------------------------------------------------------------ sky, sun, world
def sky_and_sun(sc):
    w = bpy.data.worlds.new("W_Sunrise")
    sc.world = w
    nt, ns, L = nodes(w)
    out = N(nt, "ShaderNodeOutputWorld", (600, 0))
    bg = N(nt, "ShaderNodeBackground", (300, 0))
    sky = N(nt, "ShaderNodeTexSky", (0, 0))
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(C.SUN_ELEVATION_DEG)
    # Blender's sky: sun_rotation 0 points the sun along +Y? measured: rotation is compass-like from +Y toward -X; see test
    sky.sun_rotation = math.radians(C.SUN_AZIMUTH_DEG)      # measured: 0 = north, clockwise = compass azimuth
    sky.altitude = 120
    sky.air_density = 1.6
    sky.aerosol_density = 3.0
    sky.sun_disc = True
    sky.sun_size = math.radians(0.6)
    bg.inputs["Strength"].default_value = 0.22
    L.new(sky.outputs[0], bg.inputs[0])
    L.new(bg.outputs[0], out.inputs[0])
    ld = bpy.data.lights.new("SUN", "SUN")
    ld.energy = 4.4
    ld.angle = math.radians(1.2)
    ld.color = (1.0, 0.72, 0.46)
    sun = bpy.data.objects.new("SUN", ld)
    sc.collection.objects.link(sun)
    d = Vector(C.SUN_DIR)
    sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return sky, sun


# ------------------------------------------------------------------ grass via geometry nodes
def asset_coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    c.use_fake_user = True          # instanced by geometry nodes only; not linked into the scene
    return c


def blade_collection():
    c = asset_coll("ASSET_GrassBlades")
    for i in range(6):
        h = 0.07 + i * 0.035
        w = 0.004 + (i % 3) * 0.0015
        bend = 0.04 + (i % 2) * 0.05
        me = bpy.data.meshes.new(f"blade{i}")
        segs = 4
        verts, faces = [], []
        for s in range(segs + 1):
            t = s / segs
            ww = w * (1 - t) ** 0.8
            y = bend * t * t
            verts += [(-ww, y, h * t), (ww, y, h * t)]
        for s in range(segs):
            a = 2 * s
            faces.append((a, a + 1, a + 3, a + 2))
        me.from_pydata(verts, [], faces)
        o = bpy.data.objects.new(f"BLADE_{i}", me)
        c.objects.link(o)
        o.data.materials.append(bpy.data.materials.get("M_Grass") or grass_mat())
    for i, colr in enumerate([(0.9, 0.88, 0.80), (0.95, 0.80, 0.25), (0.62, 0.48, 0.78)]):
        me = bpy.data.meshes.new(f"flower{i}")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.012)
        for v in bm.verts:
            v.co.z += 0.22 + i * 0.03
        stem = bmesh.ops.create_cone(bm, segments=4, radius1=0.0015, radius2=0.001, depth=0.22 + i * 0.03)
        for v in stem["verts"]:
            v.co.z += (0.22 + i * 0.03) / 2
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(f"FLOWER_{i}", me)
        mm = simple_mat(f"M_Flower{i}", colr, rough=0.6, noise_amt=0.1)
        o.data.materials.append(mm)
        asset_coll("ASSET_Flowers").objects.link(o)
    return c, bpy.data.collections["ASSET_Flowers"]


def grass_nodes(blades, flowers, contacts, density=420.0, flower_density=2.5, name="GN_Meadow"):
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nt = ng
    gi = N(nt, "NodeGroupInput", (-1800, 0))
    go = N(nt, "NodeGroupOutput", (1400, 0))
    L = nt.links

    def scatter(coll_, dens, seed, yoff):
        dp = N(nt, "GeometryNodeDistributePointsOnFaces", (-1500, yoff))
        dp.inputs["Density"].default_value = dens
        dp.inputs["Seed"].default_value = seed
        L.new(gi.outputs[0], dp.inputs["Mesh"])
        ci = N(nt, "GeometryNodeCollectionInfo", (-1500, yoff - 300))
        ci.inputs["Collection"].default_value = coll_
        ci.inputs["Separate Children"].default_value = True
        ci.inputs["Reset Children"].default_value = True
        ip = N(nt, "GeometryNodeInstanceOnPoints", (-1100, yoff))
        ip.inputs["Pick Instance"].default_value = True
        L.new(dp.outputs["Points"], ip.inputs["Points"])
        L.new(ci.outputs[0], ip.inputs["Instance"])
        rid = N(nt, "FunctionNodeRandomValue", (-1300, yoff - 500), data_type="INT")
        rid.inputs["Min"].default_value = 0
        rid.inputs["Max"].default_value = 99
        rid.inputs["Seed"].default_value = seed + 1
        L.new(rid.outputs[0], ip.inputs["Instance Index"])
        rz = N(nt, "FunctionNodeRandomValue", (-1300, yoff - 700), data_type="FLOAT_VECTOR")
        rz.inputs[0].default_value = (-0.12, -0.12, 0.0)
        rz.inputs[1].default_value = (0.12, 0.12, 6.283)
        rz.inputs["Seed"].default_value = seed + 2
        L.new(rz.outputs[0], ip.inputs["Rotation"])
        rs = N(nt, "FunctionNodeRandomValue", (-1300, yoff - 900), data_type="FLOAT")
        rs.inputs["Min"].default_value = 0.6
        rs.inputs["Max"].default_value = 1.35
        rs.inputs["Seed"].default_value = seed + 3
        L.new(rs.outputs[0], ip.inputs["Scale"])
        # wind sway: rotate each instance by a slowly travelling noise field
        pos = N(nt, "GeometryNodeInputPosition", (-1100, yoff - 300))
        st = N(nt, "GeometryNodeInputSceneTime", (-1100, yoff - 450))
        add = N(nt, "ShaderNodeVectorMath", (-900, yoff - 350), operation="ADD")
        cx = N(nt, "ShaderNodeCombineXYZ", (-1000, yoff - 500))
        L.new(st.outputs["Seconds"], cx.inputs["X"])
        L.new(pos.outputs[0], add.inputs[0])
        sct = N(nt, "ShaderNodeVectorMath", (-950, yoff - 600), operation="SCALE")
        L.new(cx.outputs[0], sct.inputs[0])
        sct.inputs["Scale"].default_value = 0.6
        L.new(sct.outputs[0], add.inputs[1])
        nz = N(nt, "ShaderNodeTexNoise", (-700, yoff - 350))
        nz.inputs["Scale"].default_value = 0.45
        nz.inputs["Detail"].default_value = 1.0
        L.new(add.outputs[0], nz.inputs["Vector"])
        sub = N(nt, "ShaderNodeVectorMath", (-500, yoff - 350), operation="SUBTRACT")
        L.new(nz.outputs["Color"], sub.inputs[0])
        sub.inputs[1].default_value = (0.5, 0.5, 0.5)
        amp = N(nt, "ShaderNodeVectorMath", (-300, yoff - 350), operation="MULTIPLY")
        L.new(sub.outputs[0], amp.inputs[0])
        amp.inputs[1].default_value = (0.5, 0.5, 0.0)
        # hoof contact flattening: lean instances near the MOO contact empties
        lean = None
        for ki, cobj in enumerate(contacts):
            oi = N(nt, "GeometryNodeObjectInfo", (-900, yoff - 800 - ki * 200))
            oi.inputs["Object"].default_value = cobj
            dist = N(nt, "ShaderNodeVectorMath", (-700, yoff - 800 - ki * 200), operation="DISTANCE")
            L.new(pos.outputs[0], dist.inputs[0])
            L.new(oi.outputs["Location"], dist.inputs[1])
            mr = N(nt, "ShaderNodeMapRange", (-500, yoff - 800 - ki * 200))
            mr.inputs["From Min"].default_value = 0.10
            mr.inputs["From Max"].default_value = 0.42
            mr.inputs["To Min"].default_value = 1.15
            mr.inputs["To Max"].default_value = 0.0
            L.new(dist.outputs["Value"], mr.inputs["Value"])
            if lean is None:
                lean = mr
            else:
                mx = N(nt, "ShaderNodeMath", (-300, yoff - 800 - ki * 200), operation="MAXIMUM")
                L.new(lean.outputs[0], mx.inputs[0])
                L.new(mr.outputs[0], mx.inputs[1])
                lean = mx
        tot = N(nt, "ShaderNodeVectorMath", (-100, yoff - 350), operation="ADD")
        L.new(amp.outputs[0], tot.inputs[0])
        if lean is not None:
            lv = N(nt, "ShaderNodeCombineXYZ", (-200, yoff - 600))
            L.new(lean.outputs[0], lv.inputs["X"])
            L.new(lv.outputs[0], tot.inputs[1])
        e2r = N(nt, "FunctionNodeEulerToRotation", (100, yoff - 350))
        L.new(tot.outputs[0], e2r.inputs[0])
        rot = N(nt, "GeometryNodeRotateInstances", (300, yoff))
        L.new(ip.outputs[0], rot.inputs["Instances"])
        L.new(e2r.outputs[0], rot.inputs["Rotation"])
        rot.inputs["Local Space"].default_value = True
        sv = N(nt, "GeometryNodeStoreNamedAttribute", (600, yoff), data_type="FLOAT", domain="INSTANCE")
        sv.inputs["Name"].default_value = "variation"
        rv = N(nt, "FunctionNodeRandomValue", (400, yoff - 250), data_type="FLOAT")
        rv.inputs["Seed"].default_value = seed + 9
        L.new(rot.outputs[0], sv.inputs["Geometry"])
        L.new(rv.outputs[0], sv.inputs["Value"])
        return sv

    a = scatter(blades, density, 3, 0)
    b = scatter(flowers, flower_density, 17, -1400)
    j = N(nt, "GeometryNodeJoinGeometry", (1100, 0))
    L.new(gi.outputs[0], j.inputs[0])
    L.new(b.outputs[0], j.inputs[0])
    L.new(a.outputs[0], j.inputs[0])
    L.new(j.outputs[0], go.inputs[0])
    return ng


def patch(name, c, x0, y0, x1, y1, mat, z=0.0, sub=24):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=sub, y_segments=sub, size=0.5)
    for v in bm.verts:
        v.co.x = (x0 + x1) / 2 + v.co.x * (x1 - x0)
        v.co.y = (y0 + y1) / 2 + v.co.y * (y1 - y0)
        v.co.z = z
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    o.data.materials.append(mat)
    return o


# ------------------------------------------------------------------ build
def build(sc, contacts):
    B = C.BARN
    ext = coll("ENV_EXTERIOR")
    barn = coll("ENV_BARN")
    props = coll("ENV_PROPS")
    fx = coll("ENV_ATMOSPHERE")
    sky, sun = sky_and_sun(sc)
    gm = grass_mat()
    blades, flowers = blade_collection()
    ground = patch("GROUND", ext, -160, -160, 160, 160, ground_mat(), z=0.0, sub=8)
    # hills: a ring of displaced terrain beyond 45 m
    me = bpy.data.meshes.new("HILLS")
    bm = bmesh.new()
    rings, segs = 14, 96
    for r in range(rings):
        rad = 45 + r * 22
        for s in range(segs):
            a = 2 * math.pi * s / segs
            h = (math.sin(a * 3 + 1.3) * 0.5 + math.sin(a * 7 + 0.4) * 0.25 + 0.75) * (r / rings) ** 0.8 * 26
            bm.verts.new((rad * math.cos(a), rad * math.sin(a), h - 0.4))
    bm.verts.ensure_lookup_table()
    for r in range(rings - 1):
        for s in range(segs):
            a, b2 = r * segs + s, r * segs + (s + 1) % segs
            bm.faces.new((bm.verts[a], bm.verts[b2], bm.verts[b2 + segs], bm.verts[a + segs]))
    bm.to_mesh(me)
    bm.free()
    hills = bpy.data.objects.new("HILLS", me)
    ext.objects.link(hills)
    hills.data.materials.append(simple_mat("M_Hills", (0.07, 0.10, 0.035), rough=0.95, noise_amt=0.5, scale=0.08, bump=0.0))
    for p in hills.data.polygons:
        p.use_smooth = True
    # grass patches (only where cameras look) carrying the meadow geometry nodes
    groups = {}
    for nm, (x0, y0, x1, y1, dens) in {"GRASS_MEADOW": (-21.5, -7.5, -6.0, 7.5, 520), "GRASS_MEADOW_FAR": (-6.0, -9.0, -4.7, 9.0, 160), "GRASS_BARN_NW": (-4.7, 2.4, -0.3, 9.0, 160),
                                       "GRASS_BARN_SW": (-4.7, -9.0, -0.3, -3.8, 160),
                                       "GRASS_PUDDLE_S": (-4.6, -3.8, -0.3, -2.45, 520), "GRASS_PUDDLE_N": (-4.6, 0.55, -0.3, 2.4, 300)}.items():
        g = patch(nm, ext, x0, y0, x1, y1, gm, z=0.0, sub=2)
        mod = g.modifiers.new("Meadow", "NODES")
        if dens not in groups:
            groups[dens] = grass_nodes(blades, flowers, contacts, density=dens, flower_density=dens / 160, name=f"GN_Meadow_{dens}")
        mod.node_group = groups[dens]
        g.cycles.use_motion_blur = False          # wind sway is slow; per-instance deformation blur is not worth its cost
    # dirt path from the meadow to the west entrance, puddle beside it, hoof prints near the puddle
    path = patch("PATH_DIRT", ext, -16, -1.4, -0.05, 1.4, dirt_mat(), z=0.004, sub=40)
    mud = patch("PATH_MUD", ext, -3.8, -2.45, -0.8, 0.55, dirt_mat(wet=1.0), z=0.006, sub=40)
    pu = C.PUDDLE
    me = bpy.data.meshes.new("PUDDLE")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=1.0)
    for v in bm.verts:
        v.co.x *= pu["rx"] * (1 + 0.08 * math.sin(math.atan2(v.co.y, v.co.x) * 3))
        v.co.y *= pu["ry"]
    bm.to_mesh(me)
    bm.free()
    puddle = bpy.data.objects.new("PUDDLE", me)
    ext.objects.link(puddle)
    puddle.location = (pu["x"], pu["y"], 0.008)
    puddle.data.materials.append(water_mat())
    rim = bpy.data.objects.new("PUDDLE_WET_EDGE", me.copy())
    ext.objects.link(rim)
    rim.location = (pu["x"], pu["y"], 0.0072)
    rim.scale = (1.14, 1.16, 1)
    wet = simple_mat("M_WetMud", (0.045, 0.032, 0.022), rough=0.25, noise_amt=0.4, scale=22.0, bump=0.3)
    rim.data.materials.clear()
    rim.data.materials.append(wet)
    hoof_mat = dirt_mat(wet=1.0)
    for i, (hx, hy) in enumerate([(-3.3, -1.6), (-3.05, -1.75), (-3.45, -0.2), (-1.4, -0.3), (-1.2, -1.6), (-3.6, -0.75)]):
        o = box(f"HOOFPRINT_{i}", ext, hx - 0.035, hy - 0.03, 0.0062, hx + 0.035, hy + 0.03, 0.0066, hoof_mat)
        o.scale = (1, 1, 1)
    # fences: low timber post-and-rail along the meadow
    fw = wood_mat("M_FenceWood", base=(0.12, 0.095, 0.07), grey=0.55, scale=2.0)
    for y in (-8.5, 9.0):
        for i in range(14):
            x = -32 + i * 2.2
            box(f"FENCE_POST_{y}_{i}", ext, x - 0.06, y - 0.06, 0, x + 0.06, y + 0.06, 1.0 + R.uniform(-0.05, 0.05), fw, 0.01)
        for z in (0.45, 0.85):
            box(f"FENCE_RAIL_{y}_{z}", ext, -32.0, y - 0.03, z - 0.05, -32 + 13 * 2.2, y + 0.03, z + 0.05, fw, 0.008)
    # ---------------- barn
    wallw = wood_mat("M_BarnWall", base=(0.105, 0.075, 0.05), grey=0.38, scale=1.2, planks="vertical")
    floorw = wood_mat("M_BarnFloor", base=(0.14, 0.10, 0.065), grey=0.22, scale=1.0, planks="horizontal", dust=0.35, rough=0.78)
    beamw = wood_mat("M_Beam", base=(0.09, 0.065, 0.042), grey=0.28, scale=1.4)
    roofm = simple_mat("M_Roof", (0.11, 0.09, 0.075), rough=0.85, noise_amt=0.3, scale=2)
    t = B["wall"]
    box("BARN_FLOOR", barn, B["x0"], B["y0"], -0.05, B["x1"], B["y1"], 0.0, floorw)
    # west wall with entrance opening
    e = B["entrance"]
    box("WALL_W_S", barn, B["x0"] - t, B["y0"] - t, 0, B["x0"], e["y0"], B["eave"], wallw)
    box("WALL_W_N", barn, B["x0"] - t, e["y1"], 0, B["x0"], B["y1"] + t, B["eave"], wallw)
    box("WALL_W_TOP", barn, B["x0"] - t, e["y0"], e["h"], B["x0"], e["y1"], B["eave"], wallw)
    # north wall solid, south wall with two windows
    box("WALL_N", barn, B["x0"] - t, B["y1"], 0, B["x1"] + t, B["y1"] + t, B["eave"], wallw)
    xs = [B["x0"] - t]
    for wx, z0, z1 in B["windows"]:
        box(f"WALL_S_seg{wx}", barn, xs[-1], B["y0"] - t, 0, wx - 0.45, B["y0"], B["eave"], wallw)
        box(f"WALL_S_below{wx}", barn, wx - 0.45, B["y0"] - t, 0, wx + 0.45, B["y0"], z0, wallw)
        box(f"WALL_S_above{wx}", barn, wx - 0.45, B["y0"] - t, z1, wx + 0.45, B["y0"], B["eave"], wallw)
        xs.append(wx + 0.45)
    box("WALL_S_end", barn, xs[-1], B["y0"] - t, 0, B["x1"] + t, B["y0"], B["eave"], wallw)
    # east wall: individual vertical boards with narrow gaps (sunrise light leaks), opening for the doors
    d = B["doors"]
    y = B["y0"] - t
    i = 0
    while y < B["y1"] + t - 0.01:
        w = R.uniform(0.17, 0.23)
        y1 = min(y + w, B["y1"] + t)
        gap = 0.012 if R.random() < 0.35 else 0.0
        if y1 <= d["y0"] or y >= d["y1"]:
            box(f"EAST_BOARD_{i}", barn, B["x1"], y, 0, B["x1"] + t, y1 - gap, B["eave"], wallw)
        else:
            box(f"EAST_BOARD_{i}_top", barn, B["x1"], y, d["h"], B["x1"] + t, y1 - gap, B["eave"], wallw)
        y = y1
        i += 1
    # gables + roof (closed)
    for gx, nm in ((B["x0"] - t, "W"), (B["x1"], "E")):
        me = bpy.data.meshes.new(f"GABLE_{nm}")
        vs = [(gx, B["y0"] - t, B["eave"]), (gx, B["y1"] + t, B["eave"]), (gx, 0, B["ridge"]),
              (gx + t, B["y0"] - t, B["eave"]), (gx + t, B["y1"] + t, B["eave"]), (gx + t, 0, B["ridge"])]
        me.from_pydata(vs, [], [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
        o = bpy.data.objects.new(f"GABLE_{nm}", me)
        barn.objects.link(o)
        o.data.materials.append(wallw)
    for side in (-1, 1):
        me = bpy.data.meshes.new(f"ROOF_{side}")
        yy = B["y1"] + 0.6 if side > 0 else B["y0"] - 0.6
        zz = B["eave"] - 0.35
        vs = [(B["x0"] - 0.5, 0, B["ridge"] + 0.08), (B["x1"] + 0.5, 0, B["ridge"] + 0.08), (B["x1"] + 0.5, yy, zz), (B["x0"] - 0.5, yy, zz)]
        bm = bmesh.new()
        for v in vs:
            bm.verts.new(v)
        bm.faces.new(bm.verts)
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.12)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(f"ROOF_{side}", me)
        barn.objects.link(o)
        o.data.materials.append(roofm)
    # structure: posts, tie beams, rafters
    for px in (3.0, 9.0):
        for py in (B["y0"] + 0.5, B["y1"] - 0.5):
            box(f"POST_{px}_{py}", barn, px - 0.12, py - 0.12, 0, px + 0.12, py + 0.12, B["eave"], beamw, 0.01)
        box(f"TIEBEAM_{px}", barn, px - 0.1, B["y0"], B["eave"] - 0.3, px + 0.1, B["y1"], B["eave"] - 0.05, beamw, 0.01)
    for rx in [0.6 + i * 1.4 for i in range(9)]:
        for side in (-1, 1):
            a = math.atan2(B["ridge"] - B["eave"], 4.0)
            o = box(f"RAFTER_{rx}_{side}", barn, rx - 0.05, -2.2, -0.07, rx + 0.05, 2.2, 0.07, beamw)
            o.location = (0, side * 2.0, (B["eave"] + B["ridge"]) / 2 - 0.25)
            o.rotation_euler.x = -side * a
    box("RIDGE_BEAM", barn, B["x0"], -0.1, B["ridge"] - 0.45, B["x1"], 0.1, B["ridge"] - 0.2, beamw)
    # hay bales along the north wall and the south-west corner
    hay = simple_mat("M_Hay", (0.30, 0.22, 0.085), rough=0.95, noise_amt=0.55, scale=90, bump=1.0)
    for i, (hx, hy, hz) in enumerate([(1.2, 3.3, 0), (2.15, 3.3, 0), (1.65, 3.3, 0.45), (4.4, 3.35, 0), (10.6, 3.3, 0),
                                      (10.6, 3.3, 0.45), (11.0, -3.3, 0), (1.0, -3.3, 0)]):
        box(f"HAY_{i}", props, hx - 0.45, hy - 0.25, hz, hx + 0.45, hy + 0.25, hz + 0.45, hay, 0.03)
    # training block: one solid weathered block, origin at its base centre (animated slide in +x)
    bw = wood_mat("M_TrainingBlock", base=(0.20, 0.135, 0.082), grey=0.32, scale=4.0, rough=0.62, dust=0.25)
    Bk = C.BLOCK
    blk = box("TRAINING_BLOCK", props, -Bk["d"] / 2, -Bk["w"] / 2, 0, Bk["d"] / 2, Bk["w"] / 2, Bk["h"], bw, 0.012)
    blk.location = (Bk["x"], Bk["y"], 0.0)
    # dust / wood fibre particles that shift with the block (in front of its leading lower edge)
    for i in range(26):
        o = box(f"BLOCK_DEBRIS_{i}", props, 0, 0, 0, 0.004 + R.random() * 0.006, 0.003 + R.random() * 0.004, 0.0015, bw)
        o.location = (Bk["x"] + Bk["d"] / 2 + R.uniform(0.0, 0.05), R.uniform(-Bk["w"] / 2, Bk["w"] / 2), 0.0)
        o.rotation_euler.z = R.uniform(0, 3.14)
        o["rest"] = tuple(o.location)
    # hinged double doors: pivots on the hinge lines, leaves swing inward (toward -x)
    doorw = wood_mat("M_Doors", base=(0.10, 0.072, 0.048), grey=0.42, scale=1.2, planks="vertical")
    hinges = []
    for side, hy in (("N", d["y1"]), ("S", d["y0"])):
        h = bpy.data.objects.new(f"DOOR_HINGE_{side}", None)
        barn.objects.link(h)
        h.location = (B["x1"] + 0.07, hy, 0)
        width = d["y1"] - d["y0"]
        leaf = (-width / 2 + 0.006) if side == "N" else (width / 2 - 0.006)
        o = box(f"DOOR_LEAF_{side}", barn, -0.05, min(0, leaf), 0.015, 0.05, max(0, leaf), d["h"] - 0.01, doorw, 0.008)
        o.parent = h
        for k in range(3):
            zz = 0.5 + k * 1.3
            box(f"DOOR_BRACE_{side}_{k}", barn, -0.075, min(0, leaf), zz, -0.05, max(0, leaf), zz + 0.16, doorw).parent = h
        hinges.append(h)
    # interior atmosphere: haze volume (sun beams) and dust motes
    hz = box("BARN_HAZE", fx, B["x0"] + 0.02, B["y0"] + 0.02, 0.0, B["x1"] - 0.02, B["y1"] - 0.02, B["eave"], None)
    vm = bpy.data.materials.new("M_Haze")
    nt, ns, L2 = nodes(vm)
    out = N(nt, "ShaderNodeOutputMaterial", (300, 0))
    vol = N(nt, "ShaderNodeVolumePrincipled", (0, 0))
    vol.inputs["Density"].default_value = 0.035
    vol.inputs["Anisotropy"].default_value = 0.55
    vol.inputs["Color"].default_value = (0.95, 0.92, 0.86, 1)
    L2.new(vol.outputs[0], out.inputs["Volume"])
    hz.data.materials.append(vm)
    hz.visible_shadow = False
    mist = box("MEADOW_MIST", fx, -80, -60, 0.0, -2, 60, 2.5, None)
    mm = bpy.data.materials.new("M_Mist")
    nt, ns, L3 = nodes(mm)
    out = N(nt, "ShaderNodeOutputMaterial", (300, 0))
    vol = N(nt, "ShaderNodeVolumePrincipled", (0, 0))
    vol.inputs["Density"].default_value = 0.006
    vol.inputs["Anisotropy"].default_value = 0.6
    L3.new(vol.outputs[0], out.inputs["Volume"])
    mist.data.materials.append(mm)
    mist.visible_shadow = False
    dm = simple_mat("M_DustMote", (0.85, 0.80, 0.72), rough=0.5, noise_amt=0.0)
    me = bpy.data.meshes.new("DUST")
    bm = bmesh.new()
    for i in range(1500):
        c0 = Vector((R.uniform(B["x0"] + 0.5, B["x1"] - 0.5), R.uniform(B["y0"] + 0.4, B["y1"] - 0.4), R.uniform(0.05, 3.4)))
        r = R.uniform(0.0012, 0.0026)
        ret = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=r)
        for v in ret["verts"]:
            v.co += c0
    bm.to_mesh(me)
    bm.free()
    dust = bpy.data.objects.new("DUST_MOTES", me)
    fx.objects.link(dust)
    dust.data.materials.append(dm)
    dust.visible_shadow = False
    # slow drift of the dust field
    dust.location = (0, 0, 0)
    dust.keyframe_insert("location", frame=1)
    dust.location = (0.06, -0.03, 0.05)
    dust.keyframe_insert("location", frame=C.TOTAL_FRAMES)
    # gentle natural bounce inside (warm, from the sunlit floor through the doors / gaps)
    bl = bpy.data.lights.new("BOUNCE_FILL", "AREA")
    bl.energy = 120
    bl.size = 6
    bl.color = (1.0, 0.86, 0.70)
    bo = bpy.data.objects.new("BOUNCE_FILL", bl)
    barn.objects.link(bo)
    bo.location = (7.0, 0.0, 4.0)
    return dict(sun=sun, sky=sky, block=blk, hinges=hinges, puddle=puddle, haze=hz, mist=mist, dust=dust)
