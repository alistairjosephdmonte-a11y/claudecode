# Polycab Aerorush BLDC, "The Invisible Force": 15-second, five-shot CGI film

A procedural Blender scene for a 15-second commercial in five shots. The film moves from stillness, to the remote press, to the fan accelerating, to the airflow visibly moving the curtain and plant, and ends on a wide Diwali living-room hero shot.

- **Format:** 3840 × 2160, 24 fps, 360 frames, Cycles, AgX.
- **Room:** the same procedural living room as `../polycab_superior_switch/`. `scripts/build_invisible_force.py` imports that project's builders, so room geography, props and light positions are identical between the two films.

Built in Blender 5.2.4 LTS.

## Shots

Each shot has its own animated camera, bound to a timeline marker at its first frame. The cameras are in `08_CAMERAS`.

| Shot | Frames | Camera | Lens | What happens |
|---|---|---|---|---|
| SH01 Macro blade | 1–72 | `CAM_SH01_Macro` | 85 mm f/2.8 | The fan is still. The camera tracks along a blade's underside toward the motor housing and chrome ring, lit by studio strip lights. |
| SH02 Remote press | 73–120 | `CAM_SH02_Remote` | 85 mm f/2.8 | Close-up of the remote in a hand, with the fan defocused behind it. The thumb lands on the power key at frame 108 and the remote dips 1.5 mm on the click. The fan starts at frame 110. |
| SH03 Fan orbit | 121–216 | `CAM_SH03_Orbit` | 40 mm f/4 | A low-angle 60° orbit about the fan axis, rising 0.2 m. The fan eases from rest to speed, and the room lights come up in sequence behind it. |
| SH04 Curtain and plant | 217–288 | `CAM_SH04_Curtain` | 50 mm f/4 | The sheer curtain billows gently toward the window. The plant leaves move slightly. |
| SH05 Hero wide | 289–360 | `CAM_SH05_Hero` | 30 mm f/5.6 | The camera dollies back and rises to the wide room. The last 10 frames are effectively static, leaving negative space top right for branding. |

## What is provisional (proxy)

**No approved catalogue, CAD, remote reference, logo or end slate was supplied.** The proxy items are marked in three ways:

- each has a `PROXY_NOT_PRODUCT_ACCURATE` custom property;
- each has a non-rendering `PROXY_LABEL_*` text object;
- each is listed here.

None of them should be presented as product-accurate.

- **Fan.** The Aerorush 1200 mm rebuilt from Polycab's public product photos:
  - 3 blades, short downrod, dome canopy;
  - compact motor with a chrome decorative ring;
  - Classic Black finish.

  Proportions are estimated, not taken from CAD. The blade count and geometry are fixed: the rotor is one rigid assembly and nothing is duplicated or deformed while it spins.
- **Remote.** A neutral 135 × 42 × 17 mm placeholder with an unlabelled power key, four blank keys and a status LED. No icons or functions are invented. Replace it from the approved remote reference.
- **Hand.** A procedural skin-modifier hand with thumb shape keys. It is the weakest asset in shot 2's 85 mm close-up. A scanned or sculpted hand is the recommended upgrade before final delivery.
- **Branding.** None is rendered. `10_BRANDING` holds non-rendering safe-area guides on the shot 5 camera. Logo, product name, approved claims and the standard end slate should be composited in post from official files.

## Animation controls (`09_ANIMATION_CONTROLS`)

| Controller | Properties | What it drives |
|---|---|---|
| `CTRL_Fan` | `start_frame` 110, `ramp_frames` 96, `rpm` 180, `direction` −1 | A driver expression on `FAN_Rotor` |
| `CTRL_Lights` | `wash`, `perim`, `cove`, `shelf`, `string` (0–1, eased keys) | Light energies and emission strengths |
| `CTRL_Airflow` | `start_frame` 150, `full_frame` 236, `sheer_amp_m` 0.07, `panel_amp_m` 0.012, `leaf_amp_m` 0.018 | The airflow displacement on the curtains and plant |

### Fan

- **Rotation:** the rotor angle is the exact integral of a smoothstep speed ramp. Acceleration is continuous, there are no abrupt speed changes, and motion-blur sub-frames are evaluated exactly.
- **Speed:** 180 rpm is the brief's *illustrative preview value*, not a verified specification. It works out to 45° per frame, below the 60°-per-frame point where a 3-blade rotor would appear to strobe.
- **Timing:** at the start of shot 3 the fan is at 4 % of its terminal speed. It reaches full speed at frame 206.

### Airflow (curtains and plant)

- **Method:** authored, not simulated, so it cannot go unstable.
- **How it works:**
  - The `level` channel follows the fan with a delay (smoothstep, frames 150–236).
  - Each cloth or leaf object has a Displace modifier driven by `level × amplitude`. The modifier uses slowly travelling cloud noise.
  - A vertex-group weight confines the movement: curtains move most at the hem, leaves most at their tips.
- **Direction:** the sheer is pushed toward the window, away from the string lights hung in front of it.
- **Measured motion:** up to 56 mm at the sheer hem and at most about 2 mm per frame. Leaves move about 6 mm, and the heavy side panels about 3 mm. There is no motion before frame 150, so the room is quiet in shots 1 and 2.

### Lights

| Channel | Ramps over frames |
|---|---|
| `wash` | 140–156 |
| `perim` | 146–162 |
| `cove` | 150–176 |
| `shelf` | 160–182 |
| `string` | 170–200 |

- **Always on:** the table lamp, the diyas and the dusk window light.
- **Studio lights:** the strip lights and softbox (4000 K, `LGT_Studio_*`, hidden from camera) are switched on only for shots 1–2.
- **Colour temperature:** architectural lights 3000 K, lamp 2700 K, string lights 2500 K.
- **White balance:** a partial white balance (4400 K, tint −5) keeps the room warm without the orange cast.

## Collections

`01_ARCHITECTURE`, `02_FURNITURE_AND_DECOR`, `03_AERORUSH_PRODUCT`, `04_REMOTE_AND_HAND`, `05_LIGHTING_FIXTURES`, `06_LIGHT_RIG`, `07_CURTAIN_AND_PLANT`, `08_CAMERAS`, `09_ANIMATION_CONTROLS`, `10_BRANDING`, `11_RENDER_OUTPUT`.

## Render settings

- **Engine and resolution:** Cycles on the CPU, 3840 × 2160, 24 fps, frames 1–360.
- **Sampling:** 48 adaptive samples (threshold 0.02), OpenImageDenoise, fixed seed.
- **Motion blur:** 180° shutter (0.5).
- **Colour:** AgX Base Contrast, exposure +0.9.
- **Output:** 16-bit PNG.
- **Textures:** all materials are procedural, so there are no external textures to pack.

## Build, render, encode

```bash
blender -b --factory-startup --python scripts/build_invisible_force.py   # rebuild scenes/polycab_invisible_force.blend
scripts/render_draft.sh                                                    # 960x540 review draft + MP4
setsid nohup scripts/render_master.sh > master.log 2>&1 &                  # 4K master, resumable
scripts/encode.sh deliverables/master_sequence_4k_png16 deliverables/invisible_force_master_4k.mp4 14
```
