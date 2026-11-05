import bpy, sys, os, json
a = sys.argv[sys.argv.index('--') + 1:]; out = a[0]; fr = [int(x) for x in a[1:]]
sc = bpy.context.scene; sc.render.resolution_percentage = 50; sc.render.image_settings.file_format = 'JPEG'
for s in sc.sequence_editor.sequences:
    if s.type == 'SOUND': s.mute = True
for f in fr:
    sc.frame_set(f); sc.render.filepath = os.path.join(out, f'f{f:06d}.jpg'); bpy.ops.render.render(write_still=True)
