import bpy, os
sc = bpy.context.scene; D = os.path.dirname(bpy.data.filepath); fps = sc.render.fps
ms = sorted(sc.timeline_markers, key=lambda m: m.frame)
def tc(f): s = (f - 1) / fps; return f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)):03d}'
with open(os.path.join(D, 'narration-markers.srt'), 'w') as o:
    for i, m in enumerate(ms):
        f1 = ms[i + 1].frame if i + 1 < len(ms) else sc.frame_end
        o.write(f'{i + 1}\n{tc(m.frame)} --> {tc(f1)}\n[narration marker {m.name[1:]}]\n\n')
print('markers', len(ms))
