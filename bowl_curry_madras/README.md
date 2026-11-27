# Bowl Curry, "Ten Minutes to Madras": 15-second product film (blockout stage)

**Spec:** 15 s, 24 fps, 360 frames, 3840 × 2160, Cycles. Scene units are metres.

**Status:** this is the **blockout** for approval (spec section 07). Every material is neutral clay; orange marks the provisional product cartons only. Detailed materials, the Mantaflow bake, the official artwork and final renders all wait for approval, and for the missing inputs listed below.

**File:** `scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend` is rebuilt from scratch by `scripts/build_bowlcurry.py`.

## Deliverables (blockout)

| File | What it is |
|---|---|
| `deliverables/BC_ISOMETRIC_OVERVIEW.png` | Isometric environment overview at frame 150. The ceiling, south wall and east wall are cut away. |
| `deliverables/BC_TOPDOWN_LAYOUT.png` | Top-down architectural layout with asset IDs and key dimensions. |
| `deliverables/BC_CAMERA_PATHS.png` | CAM_A and CAM_B paths in plan, with beats and 1-second ticks. Includes a strip showing camera height, lens and clearance for every frame. |
| `deliverables/BC_MILESTONE_01..07_F*.png` | The 7 camera milestone frames at 1920 × 1080: F24, 66, 102, 145, 186, 230 and 330. |
| `deliverables/BC_MILESTONES_CONTACT_SHEET.png` | All 7 milestones on one sheet. |
| `deliverables/BC_BLOCKOUT_PREVIEW_360F.mp4` | The full 360-frame preview with frame, timecode, camera, lens and beat burned in. |
| `metadata/BC_BLOCKOUT_QA_REPORT.json` | 18 automated checks (listed below). |
| `metadata/camera_paths.json` | Per-frame camera position, target, lens and clearance. |

## Shot plan

| Frames | Camera | Beat | Lens |
|---|---|---|---|
| 1–48 | CAM_A | Kitchen establishment: island, back run, dining and window on the left | 24 → 28 mm |
| 49–90 | CAM_A | Packaging reveal: carton on the island | 50 mm |
| 91–120 | CAM_A | Cooked chicken in the skillet, high three-quarter view | 50 mm |
| 121–168 | CAM_A | Sauce pour: vessel tilts in from camera-left, the stream falls and the level rises between the pieces | 65 mm |
| 169–196 | CAM_A | Spice addition: spoon tips at 176–184, and 70 grains fall and settle on the sauce | 65 mm |
| 197–240 | CAM_A | Simmering macro, pushing into the rising steam | 85 → 100 mm |
| 241–287 | CAM_B | Opens inside the steam over the serving bowl, then pulls back to the dining table | 50 → 45 mm |
| 288–360 | CAM_B | Hero hold, 73 frames (3.0 s): carton upright beside the bowl, right third clear for the end slate | 45 mm |

**Cut at 240/241:**
- On frames 237–240, the skillet steam density ramps from 8 to 40.
- CAM_B opens at density 40 inside the bowl's steam column, and the steam thins to about 1 by frame 262.
- At the hero, the steam is held at a restrained 0.6.

**Lighting:**
- A 4.0 × 2.25 m window area light on the west wall, which is camera-left in every frame (QA checked).
- Kitchen (1–240): 5600 K neutral daylight.
- Dining (241–360): 4300 K, plus a low 3600 K sun through the window for the late-afternoon feel.
- The light changes at the cut, hidden by the steam; its direction stays the same.
- A ceiling bounce light fills the room but is not visible to the camera.

## Scene structure (collections = spec asset IDs)

| Collection | Contents |
|---|---|
| `ENV_BC_01` | Room 8.0 × 5.5 × 2.8 m with a full-height west window. Kitchen back run, tall unit, uppers, sink and tap. Island 2300 × 880 with a limestone top at 910 mm and a flush induction hob. Stools and pendants. Dining table 1400 × 900, chairs, linen runner and placemat, tableware, plant. |
| `BC_MADRAS_01` | Two cartons, 120 × 45 × 190 mm: one on the island, one hero carton on the dining table. They share one mesh. The board is a 0.6 mm solidified shell with a 1.2 mm bevel. The `DIELINE` UV map is unfolded as a cross (sides, front, back, top and bottom flaps), ready for the official artwork. |
| `PROP_PAN_01` | Skillet with a 280 mm inner top diameter, 5 mm wall, 6.5 mm base, integral handle and helper lip. |
| `FOOD_CHICKEN_01` | 9 irregular pieces in the pan and 4 in the bowl. The shapes come from fixed-seed noise and each has a flattened seared base. The pieces are not animated, so no chicken goes airborne. |
| `FOOD_SAUCE_01` | Sauce level that follows the pan wall, rising frames 130–200 to 12 mm, so the pieces stay above the surface. Also the stream, the pour-vessel proxy, and the curry in the bowl. |
| `FOOD_SPICE_01` | Measuring spoon and 70 ballistic grain proxies that fall under gravity (9.81 m/s²) and settle on the sauce surface. |
| `PROP_BOWL_01`, `FOOD_RICE_01` | 180 mm serving bowl, 130 mm rice bowl, and a rice mound. |
| `FX_STEAM` | Two volume columns: noise × column falloff × a keyed `steam` object property. |
| `SIM_MANTAFLOW` | Liquid domain (res 128), inflow at the vessel spout keyed on for 128–156, and collision on the pan and chicken. **Excluded from the view layer and NOT baked** (see viscosity below). |
| `CAMERAS` | CAM_A and CAM_B: keyed location, Track-To target and lens, all Bezier (auto-clamped, eased). Depth of field focuses on the target: f/5.6 for CAM_A, f/4 for CAM_B. |
| `LIGHTS` | Window area light, late-afternoon sun, ceiling bounce. The light changes are on constant keys. |

Every object has a `final_material` custom property naming the spec material for the detail pass. Examples: warm natural oak, honed cream limestone, matte ivory plaster, brushed metal, linen, light oak floor, handmade ceramic.

## Final render settings (stored in the file, not used for the blockout)

- 3840 × 2160 at 256 samples, adaptive threshold 0.01, denoise.
- Cycles device set to GPU; Blender falls back to CPU when no GPU is configured.
- AgX view transform.
- Motion blur with a 0.5-frame (180°) shutter.
- OpenEXR multilayer, DWAA, 16-bit, written to `renders/final/`.
- Passes: depth, object index (cartons have pass index 1), Cryptomatte object, diffuse and glossy (direct, indirect, colour), volume (direct and indirect), shadow catcher, and vector.
- Cycles has had no separate "shadow" pass since 3.0. Use the shadow catcher pass, or derive shadows from the diffuse direct pass in compositing.

## QA (scripts/qa_bowlcurry.py): 18 checks, all pass

The checks cover:
- **Format and cut:** 360 frames, 24 fps, 3840 × 2160; the camera switches at frame 241.
- **Dimensions:** carton and skillet sizes; orange used on cartons only.
- **Camera motion:** Bezier interpolation; at least 5 cm clearance from solid geometry on every frame (actual minimum 0.127 m, at frame 240); no path segment passes through geometry; the window is camera-left on every frame.
- **Hero frame:** a static 3-second hold; the carton face points at the camera (cosine of at least 0.9) and 35 sample points across it are unobscured; all products are fully in frame; the right 35% of the frame is free of product.
- **Steam and food:** steam density of at least 30 on both sides of the cut and at most 1 at the hero; static chicken; spice settles on the sauce.
- **Setup:** the Mantaflow setup is present and unbaked; the final render settings are stored.

These are geometry and continuity checks only. The artwork, the look of the food and the fluid behaviour are not validated at this stage.

## Missing inputs (blocking the detail stage)

| Needed | Why |
|---|---|
| Official packaging photograph(s) / print artwork (front, back, sides, flaps) | The spec requires brand-supplied artwork applied by UV mapping. It was not supplied with this brief, so the cartons stay orange. No artwork, typography or logo has been recreated. |
| Measured carton dimensions | 120 × 45 × 190 mm is the spec's provisional value. Every carton dimension is marked PROVISIONAL in the file. |
| Inner pack format (pouch, tray?) and the pouring method | The pour uses a provisional vessel proxy (`PROP_POUCH_PROXY`). |
| Viscosity data for the prepared product | Needed to calibrate the Mantaflow sauce; see below. |
| Exterior plate or view direction | The window currently shows a neutral backdrop. |
| End-slate message and safe area | Negative space is reserved on the right third of the hero frame; the typography is added in compositing. |

## Viscosity calibration plan (before baking)

The domain holds a PROVISIONAL kinematic viscosity of 2.0 × 10⁻³ m²/s (`viscosity_base` 2.0, exponent 3). That value is a placeholder, not a calibration. Proposed procedure:

1. Prepare the product exactly as the pack instructs. Measure at the temperature it is poured at on camera, and at serving temperature.
2. Measure the following:
   - density;
   - a Bostwick consistometer reading (flow distance at 30 s), or a line-spread test;
   - if available, rotational-viscometer readings at roughly 10–100 s⁻¹ to capture shear thinning.
3. Film a reference pour at high frame rate: same height, about 150 mm, and the same flow rate as the shot.
4. Re-create the trough or line-spread test and the pour in a Mantaflow test domain at the final resolution. Sweep the viscosity across about 5 × 10⁻⁴ to 1 × 10⁻² m²/s until the spread distance over time and the stream neck-down match the reference.
5. Record the chosen value with its evidence in the dimension and parameter register. Mantaflow's viscosity is Newtonian, so shear thinning can only be approximated; any compromise will be documented.

## Deviations from the spec

| Spec | Blockout | Reason |
|---|---|---|
| Blender 4.x | Built with Blender **5.2.4** LTS | The version installed here. The .blend may not open in 4.x; the build script is plain `bpy`, and a few 5.x API names would need back-porting. |
| "360-frame animated viewport preview" | Cycles 960 × 540 at 8 samples, denoised, clay | This machine has no OpenGL/EGL, so Workbench and EEVEE can't render headless. |
| Mantaflow pour | Animated proxy stream and sauce level; the Mantaflow setup exists but is unbaked | Spec section 04 requires calibrated viscosity before final fluid properties are set. |
| Separate particle simulation for the spice | 70 keyed ballistic proxies | Deterministic and cache-free for the blockout. They will be replaced by a particle system at the detail stage. |
| Steam / simmering | Procedural volume columns; no simmer bubbles yet | Blockout scope. Bubbles and Mantaflow smoke come at the detail stage. |

## Render time (this machine: 4 CPU cores, no GPU)

| Render | Time |
|---|---|
| Blockout test frames, 640 px at 16 samples | about 13–22 s each |
| Milestones, 1920 px at 48 samples (measured) | 150–270 s each (volumes cost the most: F230 took 269 s) |
| Preview, 960 × 540 at 8 samples (measured) | about 16 s per frame, so about 1.6 h for 360 frames |
| Final, 4K at 256 samples with volumes | estimated 20–40 min per frame, so **5–10 days** for 360 frames on CPU. A GPU node is strongly recommended. |

## Commands

```bash
B=/tmp/claude-0/blender/blender-5.2.4-linux-x64/blender
$B -b --factory-startup --python scripts/build_bowlcurry.py                                   # rebuild .blend
$B -b scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend --python scripts/qa_bowlcurry.py                 # QA + camera_paths
$B -b scenes/BOWLCURRY_MADRAS_BLOCKOUT.blend --python scripts/render_overview.py -- /tmp/bc_ov 32
python3 scripts/plan_png.py /tmp/bc_ov                                                       # overview/layout/paths
scripts/render_blockout.sh                                                                   # milestones + preview
```

Helper library: `polycab_superior_switch/scripts/build_scene.py`, used for its mesh and material helpers only.
