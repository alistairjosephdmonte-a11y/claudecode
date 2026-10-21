#!/usr/bin/env python3
"""Step 8 - build the HyperFrames project: the 9:16 cut plus plain captions, nothing else.
   08_captions_project.py <project_dir> "<9x16.mp4>" <captions.json> "<Title>"
captions.json comes from 06_captions.py ([{text, start, end}], cut-clock seconds).
Captions: 2-4 words, white, the caption font, centred just under the chin, no animation, no colour words.
Writes <project_dir>/index.html and links the video into assets/. Re-running it rebuilds index.html only."""
import html, json, os, shutil, subprocess, sys

proj, video, caps_path, title = sys.argv[1:5]
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP_TOP = 1150          # just under the chin on a centred 9:16 frame; captions stay above Instagram / TikTok's bottom bar

proj = os.path.abspath(os.path.expanduser(proj))
if not os.path.exists(f"{proj}/index.html"):
    os.makedirs(os.path.dirname(proj), exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes@latest", "init", os.path.basename(proj), "--non-interactive", "--example=blank"],
                   cwd=os.path.dirname(proj), check=True, stdout=subprocess.DEVNULL,
                   env={**os.environ, "HYPERFRAMES_SKIP_SKILLS": "1"})      # do not touch the creator's installed skills
os.makedirs(f"{proj}/assets/fonts", exist_ok=True)
if os.path.isdir(f"{SKILL}/assets/fonts"):
    for f in os.listdir(f"{SKILL}/assets/fonts"):
        shutil.copy2(f"{SKILL}/assets/fonts/{f}", f"{proj}/assets/fonts/{f}")
link = f"{proj}/assets/cut.mp4"
if os.path.lexists(link): os.remove(link)
os.symlink(os.path.abspath(video), link)

dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]).decode().strip())
caps = json.load(open(caps_path))
cap_html = ""
for i, c in enumerate(caps):
    a, b = max(0.0, c["start"]), min(c["end"], dur)
    if b - a < 0.04: continue
    cap_html += (f'      <div id="cap{i}" class="clip cap" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" '
                 f'data-track-index="{10 + i % 2}"><span>{html.escape(c["text"])}</span></div>\n')

index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{html.escape(title)} - Clean Cut</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "CapFont"; src: @@FONT_CAPTION_SRC@@; font-weight: 700; }}
      body {{ margin: 0; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #cam {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .cap {{ position: absolute; inset: 0; z-index: 20; pointer-events: none; }}
      .cap span {{ position: absolute; left: 80px; right: 80px; top: {CAP_TOP}px; display: block; text-align: center;
        font-family: "CapFont", Helvetica, Arial, sans-serif; font-weight: 700; font-size: 64px; line-height: 1.05;
        letter-spacing: -0.03em; color: #FFFFFF; text-shadow: 0 3px 14px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.6); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{round(dur, 3)}">
      <video id="cam" src="assets/cut.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{round(dur, 3)}" data-track-index="0"></video>
{cap_html}    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(f"{proj}/index.html", "w").write(index)
print(f"wrote {proj}/index.html  ({len(caps)} captions, {dur:.1f}s)")
