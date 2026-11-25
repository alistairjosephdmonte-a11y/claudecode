# Polycab Fans, "The Superior Switch": 5-second Blender CGI film

A fully procedural Blender scene that follows the supplied master storyboard (`reference/master_storyboard.webp`). It is one continuous 28 mm camera move through a contemporary Indian living room:

1. **Establish (frames 1–36).** The room is subdued and the fan is still.
2. **Activate (frames 37–72).** A hand presses the remote's power key, the fan spins up, then the downlights and cove come on in sequence.
3. **Reveal (frames 73–120).** The camera pulls back to a wide hero view of the warmly lit, Diwali-ready room.

Built and rendered in Blender 5.2.4 LTS (Cycles, CPU).

## Deliverables

| Brief | File |
|---|---|
| Editable .blend | `scenes/polycab_superior_switch.blend`, rebuilt by `scripts/build_scene.py` |
| Packed textures | None to pack: every material is a procedural node tree (`validate.py` checks for external files) |
| Image sequence (master) | `deliverables/master_sequence_png16/frame_0001.png` … `frame_0120.png`, 1920 × 1080, 16-bit PNG |
| MP4 review | `deliverables/superior_switch_review_1080p.mp4` (H.264, CRF 16, 24 fps) |
| Final branded master | **Not produced yet.** It needs the official artwork; see [Branding](#branding) |
| Camera/animation documentation | This README, plus `metadata/camera_animation.json` |
| QC | `metadata/validation.json` (17 checks) |

## Accuracy and what is provisional

- **Fan.** The Polycab Aerorush 1200 mm was rebuilt from Polycab's public product photos and specifications (polycab.com product p-69875 and its colour variants):
  - 1200 mm sweep, 3 aluminium blades, 360 rpm maximum;
  - the "unique decorative motor ring", modelled in chrome;
  - the Classic Black finish.

  No CAD or approved catalogue references were supplied. The proportions are read from photos (motor about 210 mm across, short downrod, dome canopy), so they are **not manufacturing-accurate**. The storyboard's glowing ring under the motor is not on the real product, so it was not modelled.
- **No branding is rendered on the fan.** The real canopy carries a small POLYCAB wordmark. It is left blank until official artwork is supplied.
- **Remote.** No Aerorush remote reference was supplied. The remote is a neutral 135 × 42 × 17 mm placeholder with a power key, four unlabelled keys and a status LED. The only marking is a moulded power symbol.
- **Hand.** It is a procedural skin-modifier hand with a medium-brown skin tone. Its "Thumb_Hover" and "Thumb_Press" shape keys drive the press. It is the weakest element, so it stays in soft focus in the foreground while the camera focuses on the fan. A scanned or sculpted hand would be the upgrade.

## Scene organisation

| Collection | Contents |
|---|---|
| `01_ARCHITECTURE` | Floor (1200 × 600 stone), walls, left-wall window and frame, false ceiling with a 3.00 m tray, cove upstand, skirting, 58 walnut slats |
| `02_INTERIOR_ASSETS` | L-shaped woven sofa with rust-red and ivory cushions; walnut coffee table, rug, books, brass urli with marigolds; side table and lamp; curtains and sheer; console; shelves; décor; plants; 9 diyas |
| `03_POLYCAB_AERORUSH` | `FAN_Mount` holds the canopy, downrod and top cover, which stay still. `FAN_Rotor` holds the motor shell, chrome ring, bottom cap, blade holders, 3 blades and rivets, which rotate. |
| `04_REMOTE_CONTROL` | `REMOTE_*` and `HAND_Right` (skin modifier + shape keys), sleeve cuff, `HAND_Rig_CamSpace` |
| `05_LIGHTING_FIXTURES` | Downlight trims, reflectors and lenses; cove LED strip; shelf LED strips; string-light bulbs and wire; lamp shade; diya flames |
| `06_LIGHT_RIG` | Real light objects: 10 spot downlights, 4 cove area lights, 3 shelf area lights, 5 string-light points, table lamp, 9 diya points, dusk window fill, window portal, neutral fill |
| `07_CAMERA_RIG` | `CAM_Hero`, `CAM_Look_Target`, `CAM_Path_Preview` (path display only, not rendered) |
| `08_ANIMATION_CONTROLS` | `CTRL_Fan` and `CTRL_Lights` (below) |
| `09_BRANDING` | Non-rendering guides marking the logo and message safe areas |
| `10_RENDER_SETTINGS` | `RENDER_Settings_Doc`, whose custom properties record the settings |

## Animation (24 fps, 120 frames)

### Camera

`CAM_Hero` uses a fixed 28 mm lens on a 36 mm sensor at f/5.6. Its location is keyed with Bézier curves, and a Track To constraint follows a keyed look target. Focus is keyed to stay on the fan.

| Frame | Camera (m) | Look target (m) | Beat |
|---|---|---|---|
| 1 | (0.30, −2.55, 1.02) | (−0.25, 1.40, 1.95) | Low, intimate. The fan is in the upper frame and the camera is already gliding forward. |
| 36 | (0.12, −1.30, 1.18) | (−0.22, 1.00, 2.20) | Pushing in and starting to tilt up |
| 54 | (0.00, −0.45, 1.38) | (−0.25, 0.65, 2.62) | Closest point, looking up at the fan |
| 66 | (0.02, −0.52, 1.40) | (−0.25, 0.66, 2.58) | Holding while the lights come up |
| 112–120 | (0.05, −2.75, 1.58) | (−0.25, 1.05, 1.95) | Pulled back and slightly raised to the wide hero view. The last 8 frames are effectively static. |

- **Speed:** peak 1.64 m/s during the pull-back. The camera is stationary (0.001 m/s) on the final frame.
- **Clearance:** at least 0.44 m from all geometry.
- **No cuts:** there are no cuts, zooms or lens changes.

### Fan (`CTRL_Fan`)

The rotor angle is a driver expression, not baked keys, so motion-blur sub-frames are evaluated exactly.

- The speed eases from 0 to `rpm` with a smoothstep over `ramp_frames`, starting at `start_frame`. The angle is the integral of that speed.
- The result is continuous acceleration and then a constant terminal angular velocity.

The defaults are:

| Property | Default |
|---|---|
| `start_frame` | 47 |
| `ramp_frames` | 44 |
| `rpm` | 150 |
| `direction` | −1 (counter-clockwise seen from below) |

- **Why 150 rpm:** it is a mid setting on the Aerorush's 25-step control and works out to 37.5° per frame.
- **Why not 360 rpm:** at the 360 rpm maximum a blade moves 90° per frame. A 3-blade fan aliases at 60° per frame, so it would appear to strobe or spin backwards on camera.
- **Changing it:** edit the properties on `CTRL_Fan`. No re-bake is needed.

### Remote press

- The hand enters from the lower left at frame 36 and is lowered out of frame by frame 62.
- The thumb lands on the power key at frame 44 and lifts at frame 50.
- The fan starts at frame 47.

### Light cues (`CTRL_Lights`)

Each channel is a 0–1 custom property with eased Bézier keys. Light energies and emission strengths are driven from it.

| Channel | Ramps over frames | What it drives |
|---|---|---|
| `wash` | 56–66 | Four downlights washing the slat wall and shelves |
| `perim` | 60–70 | Six perimeter downlights |
| `cove` | 63–80 | Tray cove: four area lights and the LED strip |
| `shelf` | 68–82 | Under-shelf LEDs |
| `string` | 76–96 | Diwali curtain string lights |

- **Separate cue:** the first light starts 9 frames after the fan, so the lights read as a separate cue rather than something the fan remote switches.
- **Always on:** the table lamp, the diyas and the dusk window light are lit throughout.
- **Colour temperature:**
  - architectural lights: 3000 K;
  - table lamp: 2700 K;
  - string lights: 2500 K;
  - diya flames: 1850 K.

## Render settings

- **Engine and resolution:** Cycles on the CPU, 1920 × 1080, 24 fps.
- **Sampling:** 64 adaptive samples (threshold 0.02), OpenImageDenoise, fixed seed so denoised noise does not shimmer between frames.
- **Light paths:** 8 bounces (4 diffuse, 4 glossy). Indirect light clamped at 6. Caustics off.
- **Motion blur:** on, 180° shutter (0.5).
- **Colour:** AgX, Base Contrast look, exposure +0.9.
- **Output:** 16-bit PNG.

The machine is a 4-core CPU with no GPU. A 96-sample test frame took 6 minutes, so the master uses 64 samples with denoising.

## Branding

No official logo, end slate, typeface or product-title artwork was supplied, so none is rendered or drawn. The brief says not to invent or distort lettering.

- **Safe areas:** the end composition leaves negative space top right for the category logo, and at right-centre for the product name and "Feel the superior difference".
- **Guides:** both areas are marked by the non-rendering guides in `09_BRANDING`, using normalised boxes inside title-safe.
- **Compositing:** `scripts/brand_master.py` places the supplied files, scaled to fit without stretching and with fade-ins, to make the branded master:

```bash
python3 scripts/brand_master.py <official_logo.png> <official_end_slate.png>
scripts/encode_review.sh deliverables/branded_sequence deliverables/superior_switch_branded_1080p.mp4
```

## Rebuild, render, validate

```bash
blender -b --factory-startup --python scripts/build_scene.py
blender -b scenes/polycab_superior_switch.blend --python scripts/validate.py
setsid nohup scripts/render_master.sh > master.log 2>&1 &      # all 120 frames, resumable
scripts/encode_review.sh
```

For an OpenEXR (half-float) master instead of PNG:

```bash
blender -b scenes/polycab_superior_switch.blend --python scripts/render_frames.py -- 1-120 1920 64 deliverables/master_sequence_exr exr
```

## Validation

`scripts/validate.py` runs 17 checks and writes `metadata/validation.json`.

| Area | Checks |
|---|---|
| Collections | The 10 required collections exist and no objects are loose |
| Fan geometry | 3 blades, 1.200 m sweep, blades 0.31 m below the tray and 2.69 m above the floor, blade tips 0.9 m inside the tray edge |
| Fan motion | Monotonic spin-up, then constant speed. Below the 60°-per-frame aliasing limit. |
| Light cues | No reversals and at most 0.15 change per frame (no flicker). Lights start after the fan. |
| Camera | Clearance and speed limits; fixed lens |
| Remote | The thumb is within 2.5 mm of the power key at frame 46. Remote is 135 mm, 0.11 of the fan sweep. |
| Room continuity | Nothing except the rigs moves between frames 1, 60 and 120. No duplicated objects. |
| Intersections | No furniture-to-furniture or furniture-to-architecture overlaps, apart from intended resting contacts |
| External files | None: there are no external image files |

Pass rendered frame paths after `--` to also check for clipped pixels.
