import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]; s0, s1, out = int(a[0]), int(a[1]), a[2]
sc = bpy.context.scene; sc.frame_start, sc.frame_end = s0, s1
r = sc.render; r.image_settings.file_format = 'FFMPEG'; r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'
r.ffmpeg.constant_rate_factor = os.environ.get('CRF', 'PERC_LOSSLESS'); sc.render.resolution_percentage = int(os.environ.get('PCT', '100')); r.ffmpeg.ffmpeg_preset = 'GOOD'; r.ffmpeg.audio_codec = 'NONE'; r.filepath = out
for s in sc.sequence_editor.sequences:
    if s.type == 'SOUND': s.mute = True
bpy.ops.render.render(animation=True)
