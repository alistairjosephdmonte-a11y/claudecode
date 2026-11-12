"""Matte clay materials, emissives and image materials (one cache per name)."""
import os

import bpy

import config as C

_lib = {}


def _new(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links


def clay(name, col, rough=0.85, metal=0.0, spec=0.3):
    if name in _lib:
        return _lib[name]
    m, n, _ = _new(name)
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = C.rgb(col) if isinstance(col, str) else col
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    m.diffuse_color = b.inputs["Base Color"].default_value
    _lib[name] = m
    return m


def emit(name, col, strength=4.0):
    if name in _lib:
        return _lib[name]
    m, n, l = _new(name)
    n.remove(n["Principled BSDF"])
    e = n.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = C.rgb(col) if isinstance(col, str) else col
    e.inputs["Strength"].default_value = strength
    l.new(e.outputs[0], n["Material Output"].inputs[0])
    _lib[name] = m
    return m


def image(name, file, rough=0.7, emission=0.0, metal=0.0):
    if name in _lib:
        return _lib[name]
    m, n, l = _new(name)
    b = n["Principled BSDF"]
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(C.P["tex"], file), check_existing=True)
    l.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emission:
        l.new(t.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emission
    _lib[name] = m
    return m


def get(name):
    if name in _lib:
        return _lib[name]
    presets = {"eye": ("#141014", 0.3), "mouth": ("#3a1418", 0.8)}
    return clay(name, *presets[name])
