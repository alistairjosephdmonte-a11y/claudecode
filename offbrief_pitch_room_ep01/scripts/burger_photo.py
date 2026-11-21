"""Builds and renders the static 'premium burger' food photo shown on the pitch-room monitor (shot 08).
No ketchup, no red sauce. Output: textures/burger_slide.png (1920x1080, Cycles CPU).
    blender -b --factory-startup --python scripts/burger_photo.py
"""
import math
import os
import random

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "textures", "burger_slide.png")
rnd = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, col, rough=0.5, sss=0.0, coat=0.0, noise=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Coat Weight"].default_value = coat
    if noise:
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = noise[0]
        n.inputs["Detail"].default_value = 6
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].color = (*noise[1], 1)
        r.color_ramp.elements[1].color = (*col, 1)
        nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
        nt.links.new(r.outputs["Color"], p.inputs["Base Color"])
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = 0.25
        nt.links.new(n.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def add(o, m):
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


BUN = mat("bun", (0.36, 0.14, 0.03), 0.38, 0.1, 0.3, (14, (0.62, 0.32, 0.08)))
BUN_IN = mat("bun_inside", (0.55, 0.30, 0.10), 0.6, 0.0, 0.0, (14, (0.75, 0.55, 0.30)))
SEED = mat("sesame", (0.93, 0.86, 0.68), 0.45)
PATTY = mat("patty", (0.16, 0.075, 0.04), 0.55, 0.0, 0.2, (40, (0.07, 0.035, 0.02)))
CHEESE = mat("cheese", (0.98, 0.62, 0.08), 0.25, 0.4, 0.3)
LETTUCE = mat("lettuce", (0.35, 0.62, 0.12), 0.4, 0.3, 0.2, (25, (0.62, 0.8, 0.3)))
ONION = mat("red_onion", (0.55, 0.22, 0.52), 0.25, 0.3, 0.4, (12, (0.92, 0.85, 0.92)))
BOARD = mat("board", (0.30, 0.17, 0.08), 0.55, 0.0, 0.0, (3, (0.2, 0.1, 0.05)))

# bottom bun
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.056, depth=0.026, location=(0, 0, 0.013))
o = add(bpy.context.object, BUN_IN)
bv = o.modifiers.new("b", "BEVEL"); bv.width, bv.segments = 0.008, 4
# lettuce ruffle
bpy.ops.mesh.primitive_circle_add(vertices=96, radius=0.066, fill_type="NGON", location=(0, 0, 0.0285))
o = bpy.context.object
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=6); bpy.ops.object.mode_set(mode="OBJECT")
for v in o.data.vertices:
    r = v.co.xy.length
    a = math.atan2(v.co.y, v.co.x)
    v.co.z = -max(0, r - 0.05) * 0.9 + 0.004 * math.sin(a * 13) * (r / 0.066) ** 3
sol = o.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.0015
add(o, LETTUCE)
# patty
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.061, depth=0.022, location=(0, 0, 0.042))
o = bpy.context.object
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=3); bpy.ops.object.mode_set(mode="OBJECT")
tex = bpy.data.textures.new("pattyN", "CLOUDS"); tex.noise_scale = 0.012
d = o.modifiers.new("d", "DISPLACE"); d.texture, d.strength = tex, 0.0015
bv = o.modifiers.new("b", "BEVEL"); bv.width, bv.segments = 0.006, 3
add(o, PATTY)
# cheese slice draping over the patty edge
bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=0.118, location=(0, 0, 0.0545))
o = bpy.context.object
o.rotation_euler.z = 0.35
for v in o.data.vertices:
    r = v.co.xy.length
    over = max(0.0, r - 0.056)
    v.co.z = max(-0.016, -over * 0.9 - over * over * 15)
sol = o.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.0025
add(o, CHEESE)
# red onion rings
for i in range(4):
    a = i * 1.7
    bpy.ops.mesh.primitive_torus_add(major_radius=0.022 + 0.004 * i, minor_radius=0.0035,
                                     location=(0.02 * math.cos(a), 0.02 * math.sin(a), 0.059 + 0.001 * i))
    o = bpy.context.object
    o.scale.z = 0.6
    o.rotation_euler = (rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 0)
    add(o, ONION)
# top bun dome
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=0.059, location=(0, 0, 0.062))
o = bpy.context.object
o.scale.z = 0.62
add(o, BUN)
for _ in range(70):
    th = rnd.uniform(0, 2 * math.pi)
    ph = math.acos(rnd.uniform(0.25, 1.0))
    n = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
    p = Vector((n.x * 0.059, n.y * 0.059, 0.062 + n.z * 0.059 * 0.62))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.0022, location=p)
    s = bpy.context.object
    s.scale = (1.0, 0.55, 0.35)
    s.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    s.rotation_euler.rotate_axis("Z", rnd.uniform(0, 3.14))
    add(s, SEED)
# board + backdrop
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.15, depth=0.018, location=(0, 0, -0.009))
o = add(bpy.context.object, BOARD)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -0.018))
add(bpy.context.object, mat("tabletop", (0.09, 0.06, 0.045), 0.4))
bg = mat("backdrop", (0.06, 0.035, 0.025), 0.8)
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0.9, 0.4), rotation=(math.radians(90), 0, 0))
add(bpy.context.object, bg)
for i in range(7):   # warm out-of-focus practicals behind
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(rnd.uniform(-0.6, 0.6), rnd.uniform(0.75, 0.85), rnd.uniform(0.05, 0.25)))
    em = bpy.data.materials.new(f"bokeh{i}"); em.use_nodes = True
    nt = em.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1.0, 0.62, 0.3, 1); e.inputs["Strength"].default_value = 3
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
    bpy.context.object.data.materials.append(em)

# lights
def area(loc, rot, size, power, col):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object.data
    l.size, l.energy, l.color = size, power, col

area((-0.35, -0.25, 0.35), (math.radians(55), 0, math.radians(-55)), 0.35, 6, (1.0, 0.92, 0.82))  # key
area((0.4, 0.35, 0.25), (math.radians(-70), 0, math.radians(-130)), 0.25, 5, (1.0, 0.75, 0.5))   # rim
area((0.35, -0.4, 0.05), (math.radians(85), 0, math.radians(40)), 0.4, 1.0, (0.9, 0.92, 1.0))     # fill
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.05

bpy.ops.object.camera_add(location=(0, -0.62, 0.16))
cam = bpy.context.object
cam.data.lens = 60
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 2.8
cam.data.dof.focus_distance = 0.63
cam.rotation_euler = (Vector((0, 0, 0.06)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam

sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
