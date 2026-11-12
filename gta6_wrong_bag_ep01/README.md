# THE LAST JOB · EP01 · THE WRONG BAG — block-render previs

A 10-second Blender EEVEE block previs: exactly 300 frames (0–299) at 30 fps, 1920×1080, with ten hard cuts at frames 30, 60, … 270.

The brief targets Blender 4.x. This project was built and rendered in Blender 5.2. It uses EEVEE, armatures with IK constraints, shape keys, damped-track constraints and sequencer sound strips.

## Deliverables

- **`scenes/LASTJOB_EP01_WRONG_BAG.blend`** — the scene. It contains:
  - **Collections:** `LOCATION_01_PETROL_STATION`, `CAR_01`, `BAG_01`, `JASON_01`, `LUCIA_01`, `HELI_01`, `POLICE_DISTANT`, `FX_ATMOS` and `CAMERAS`.
  - **Cameras:** `CAM_01`–`CAM_10`, bound to timeline markers at each cut.
  - **Timeline annotations:**
    - Markers for each dialogue line's start and end, every phoneme, the zip start and the 15 cm point, the tag pinch, the frame the tag becomes legible, and the searchlight beats.
  - **Sound strips:** each dialogue line is a separate strip in the sequencer (`DLG_JASON_01` …), placed at its brief frame.
- **`delivery/LASTJOB_EP01_WRONG_BAG_previs_1920x1080_30fps.mp4`** — the 16:9 preview with the WAV mix.
- **`delivery/LASTJOB_EP01_WRONG_BAG_previs_1080x1920_9x16.mp4`** — the optional 9:16 version. It is the centre 608×1080 column of the 16:9 frame, scaled to 1080×1920.
- **`audio/LASTJOB_EP01_mix.wav`** — 48 kHz stereo mix.
  - It stops dead at frame 300 for the hard cut.
  - The stems are in `audio/stems/`, and each dialogue line is also a separate file in `audio/dialogue/`.
- **`delivery/LASTJOB_EP01_contact_sheet.png`** and **`delivery/LASTJOB_EP01_shot_list.csv`**.
- **`metadata/`**:
  - `qc_report.json` — the brief's QC list, checked automatically.
  - `lipsync.json` — per-frame jaw envelope and phoneme markers.
  - `audio_cues.json`
  - `build_log.json`

## QC (scripts/qc.py; 10/10 pass)

| Check | How it is verified |
|---|---|
| Exact duration | Frames 0–299 at 30 fps = 10.000 s. The MP4 is encoded to exactly 300 frames, and the WAV is exactly 10.000 s. |
| Cuts and cameras | The markers sit at 0, 30, … 270 and are bound to `CAM_01`…`CAM_10`. Each lens matches the brief, and no lens is animated, so there is no zoom. |
| Identity | Each character keeps the same named parts and wardrobe materials throughout. |
| Product dimensions | Measured bounding boxes:<br>• PS5 390 × 260 × 104 mm<br>• DualSense 160 × 106 × 66 mm<br>• GTA case 135 × 170 × 14 mm<br>• Tag 95 × 50 mm |
| Eyelines | In both two-way exchanges, each character's pupils aim within 12° of the other character's eyes. |
| Car axis | Every interior close-up is shot from the windshield side, with Jason screen-right and Lucia screen-left in all of them. |
| Tag legibility (f220–239) | The text faces `CAM_08` (dot ≥ 0.993). All 9 sample points on the text are unobstructed. The text line is ≥ 149 px tall. |
| Prop positions | The products stay inside the bag on every frame, and the tag cord stays at its 4 cm length (max 4.1 cm measured). |
| Lip-sync | Jaws move only inside the brief's line windows, and the jaw follows each line's loudness envelope (r ≥ 0.99). Lines don't overlap, and each sound strip starts on its line's first frame. |
| Zero clipping | Mesh-to-mesh tests run every 2nd frame and cover:<br>• the products against each other and the bag<br>• the tag against the bag and the products<br>• the bag against the car interior<br>• both characters against the car, each other and the bag<br>• the car against the pumps and pillars<br>• the helicopter against the canopy |

## Staging decisions (where the brief left room)

- **Close-ups (CAM_02/03/06/07/10, plus the CAM_04 insert):** these are hood mounts shooting back through the windshield. Inside the cabin a 65–85 mm lens can't frame a head-and-shoulders close-up. All interior cameras stay on the windshield side of the Jason–Lucia line.
- **CAM_05 and CAM_08:** these look in through the open passenger window, as the car's side windows are rolled down.
- **SHOT_04:** Jason pulls the zipper 15 cm left-to-right in the characters' frame, from the driver's side toward Lucia, f094–f116. Because the camera faces back into the car, this reads right-to-left on screen.
- **SHOT_05:** Lucia finishes the zip toward her own end (f122–131), and the flaps open (f132–144) to reveal the products in foam.
  - The far end of the zipper is out of Jason's reach.
  - Only one hand is ever on the zipper pull.
- **SHOT_09:** the helicopter approaches down the car's centreline, so the beam clears the canopy pillars and slab. The beam crosses the ground and hood onto the windshield between f246 and f264. In SHOT_10 it sweeps across Jason's face between f274 and f292.

## Placeholders

- **No licensed marks are reproduced.** There are no PlayStation, GTA or Rockstar logos. The products are modelled from their real-world dimensions, and the case cover reads `GTA_CASE_01 / LICENSED ART PLACEHOLDER`. Swap in the approved art at final.
- **Characters:** Jason and Lucia are clay proxies matching the uploaded sheets' proportions, wardrobe, hair and accessories. They are not likenesses.
- **Dialogue:** a robotic espeak-ng guide, fitted to the exact frame windows, for actors to replace. All SFX and ambience are synthesized.

## Rebuild

```bash
python3 scripts/textures.py && python3 scripts/dialogue.py
```

```bash
blender -b --factory-startup --python scripts/build.py
```

```bash
python3 scripts/audio.py
```

```bash
blender -b scenes/LASTJOB_EP01_WRONG_BAG.blend --python scripts/qc.py
```

```bash
blender -b scenes/LASTJOB_EP01_WRONG_BAG.blend --python scripts/render.py -- 0 299
```

```bash
python3 scripts/deliver.py
```
