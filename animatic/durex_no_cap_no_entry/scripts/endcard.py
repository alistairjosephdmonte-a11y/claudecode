"""End card (frames 673-720): clean geometry layer in its own scene with LABELLED PLACEHOLDERS.

Brand assets must be externally supplied and approved. Nothing here approximates the Durex logo or
packaging: the placeholders are neutral grey shapes whose object names / custom properties flag them.
The only on-screen text in the film is the campaign line.
"""
import bpy
import bmesh
from mathutils import Vector

from common import bm_box, mesh_from_bm, new_object, emission, principled, srgb

CAMPAIGN_LINE = "NO COVER. NO ENTRY."


def build_endcard(main_scene):
    sc = bpy.data.scenes.new("END_CARD")
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = main_scene.render.fps
    sc.frame_start, sc.frame_end = 1, 48
    coll = bpy.data.collections.new("END_CARD_LAYER")
    sc.collection.children.link(coll)
    w = bpy.data.worlds.new("WORLD_ENDCARD")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = w

    bg = emission("MAT_ENDCARD_BG", "#05070D", 1.0)
    ph = principled("MAT_PLACEHOLDER_NEUTRAL_GREY", "#7A7A7A", rough=0.6)
    ph_flat = emission("MAT_PLACEHOLDER_LOGO_FLAT_GREY", "#6E6E6E", 1.0)
    txt = emission("MAT_ENDCARD_CAMPAIGN_LINE_WHITE", "#F2F2F2", 1.0)

    bm = bmesh.new()
    bm_box(bm, (8.0, 0.01, 4.5), (0, 0.6, 0))
    new_object("ENDCARD_BACKGROUND", mesh_from_bm("ENDCARD_BACKGROUND", bm, False), coll, [bg])

    bm = bmesh.new()
    bm_box(bm, (1.25, 0.02, 0.42), (0, 0, 0), bevel=0.06, segs=4)
    logo = new_object("PLACEHOLDER__DUREX_LOGO__APPROVED_ASSET_REQUIRED", mesh_from_bm("PH_LOGO", bm), coll, [ph_flat])
    logo.location = (0, 0, 0.78)
    logo["asset_status"] = "PLACEHOLDER - replace with approved Durex logo artwork (vector/plate) before final"

    bm = bmesh.new()
    bm_box(bm, (0.7, 0.2, 0.95), (0, 0, 0), bevel=0.012)
    pack = new_object("PLACEHOLDER__CONDOM_PACKSHOT__APPROVED_ASSET_REQUIRED", mesh_from_bm("PH_PACK", bm), coll, [ph])
    pack.location = (0, 0.1, -0.08)
    pack.rotation_euler.z = 0.28
    pack["asset_status"] = "PLACEHOLDER - replace with official approved packshot render/plate before final"

    cu = bpy.data.curves.new("ENDCARD_CAMPAIGN_LINE", "FONT")
    cu.body = CAMPAIGN_LINE
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = 0.2
    cu.space_character = 1.12
    t = new_object("ENDCARD_CAMPAIGN_LINE", cu, coll)
    cu.materials.append(txt)
    t.location = (0, -0.05, -0.86)
    t.rotation_euler.x = 1.5708
    t["note"] = "Only on-screen text in the film. Font is Blender default: swap for approved campaign typeface."

    ld = bpy.data.lights.new("ENDCARD_SOFTBOX", "AREA")
    ld.energy = 120
    ld.size = 3.0
    lo = bpy.data.objects.new("ENDCARD_SOFTBOX", ld)
    coll.objects.link(lo)
    lo.location = (1.2, -3.0, 1.8)
    lo.rotation_euler = (Vector((0, 0, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()

    cd = bpy.data.cameras.new("ENDCARD_LAYER_CAM")
    cd.type = "ORTHO"
    cd.ortho_scale = 4.4
    cam = bpy.data.objects.new("ENDCARD_LAYER_CAM", cd)
    coll.objects.link(cam)
    cam.location = (0, -6, 0)
    cam.rotation_euler = (1.5708, 0, 0)
    cam["note"] = "Graphics-layer camera for the end card (not a story camera; story cameras are CAM_01..CAM_10)."
    sc.camera = cam
    return sc
