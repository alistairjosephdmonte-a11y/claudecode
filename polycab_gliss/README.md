# Polycab Lighting, Gliss "In the Best Light": 15-second, 10-shot CGI film

An editable Blender build of the master storyboard (`reference/master_storyboard.webp`) and the JSON production brief.

- **Format:** 3840 × 2160 at 24 fps, 360 frames, Cycles.
- **File:** everything lives in one file, `scenes/POLYCAB_GLISS_MASTER.blend`, rebuilt by `scripts/build_gliss.py`.
- **Version:** built in Blender 5.2.4 LTS, headless, on a 4-core CPU with no GPU.

**Status: provisional inspection stage.** Only previews and inspection stills have been rendered. The brief gates final rendering behind approval. **The product is not dimensionally certified:** no manufacturer dimensions exist.

## Deliverables

| Brief item | File | Status |
|---|---|---|
| POLYCAB_GLISS_MASTER.blend | `scenes/POLYCAB_GLISS_MASTER.blend` | Editable. The artwork texture is packed. Every other material is procedural. |
| GLISS_DIMENSION_REGISTER.json | `metadata/` | Every value is PROVISIONAL. Manufacturer fields are `null`. |
| GLISS_PRODUCT_VALIDATION_FRONT / SIDE / TOP.png | `deliverables/` | Orthographic, 320 mm frame width, with a 50 mm scale bar |
| GLISS_PRODUCT_OFFICIAL_OVERLAY.png | `deliverables/` | Camera-matched silhouette overlay against the official photograph |
| GLISS_PRODUCT_MACRO.png | `deliverables/` | Shot 2, frame 48. 1080p preview quality. |
| GLISS_ENVIRONMENT_MASTER.png | `deliverables/` | Shot 9, frame 276, BEAUTY layer with no cast |
| GLISS_LIGHTING_BEFORE / AFTER.png | `deliverables/` | Frames 84 and 85: same camera, exposure and white balance |
| GLISS_CAMERA_PATH_PLAN.png | `deliverables/` | Top view of every architecture camera path and the walkthrough |
| GLISS_ARCHITECTURAL_WALKTHROUGH_PREVIEW.mp4 | `deliverables/` | 10 s, 240 frames, 960 × 540 preview |
| GLISS_15S_MASTER_ANIMATIC.mp4 | `deliverables/` | 15 s, 360 frames, 960 × 540 preview, cast proxies visible |
| GLISS_FINAL_PACKSHOT.png | `deliverables/` | Frame 300, product only. Brand artwork is not supplied (see below). |
| GLISS_TECHNICAL_QA_REPORT.json | `metadata/` | 13 checks, all passing. The product dimension report is NOT VERIFIED throughout. |

All renders are preview quality:
- **Stills:** 1920 × 1080, 48 samples, PNG.
- **Animation:** 960 × 540, 16 samples.

The final settings from the brief (4K, 256 samples, multilayer EXR with passes) are stored in the scenes but have **not been run**.

## Source authority and what is verified

**Verified on polycab.com p-64543 (fetched 27 Nov 2026):**

| Field | Value |
|---|---|
| Product | Gliss COB Surface Track Light (BLACK HSG) |
| Specifications table | "3000K, Warm White", Wattage "7", Warranty "2 Years" |
| Body | "sleek aluminium body" |
| Illumination | "focused, anti-glare illumination through recessed COB technology" |
| Mounting | "ceilings or walls" |
| Product photograph | One 400 × 400 px image |

**Not found anywhere supplied:**
- any dimension;
- beam angle, lumens, CRI, IES file;
- tilt or rotation limits.

The page's "Highlights" show an unlabelled "1200", which is not used.

The 6500 K and 4000 K variants come from the brief. They are not confirmed on the fetched page, and the catalogue PDF named in the brief was not supplied.

## Product master (`01_GLISS_PRODUCT_MASTER`)

`scripts/gliss_product.py` holds the dimension register and `rebuild_gliss_product()`. The module is also embedded in the .blend as the text block `gliss_product.py`.

**Register:**
- Proportions are fitted to the official photograph, normalised to housing diameter = 1.0.
- Absolute size comes from a separate **world-scale control**: housing Ø60 mm. That number is read from the storyboard sheet, which is generated imagery and the lowest-priority source.
- `solve_world_scale()` rescales everything as soon as one verified measurement is entered in `verified_manufacturer_dimensions_mm`. Every other value stays PROVISIONAL until it is replaced individually.

**Parts:**

| Collection | Parts |
|---|---|
| `GLISS_MASTER_MOUNT` | `GLISS_BASE` (drum), `GLISS_BASE_BOSS`, `GLISS_STEM`, `GLISS_BASE_DETAILS` (the two screw recesses and four vent slots visible in the photograph) |
| `GLISS_MASTER_HEAD` | `GLISS_HOUSING` (hollow, with a recessed cavity), `GLISS_FRONT_RIM`, `GLISS_REFLECTOR` (faceted, 36 × 6 flat facets), `GLISS_COB` (one emitter disc), `GLISS_PIVOT` (the pad where the stem meets the housing) |

**Instances:**
- Every visible Gliss is a collection instance of these two collections: the studio product, both installed fixtures and the walkthrough pair. A rebuild updates all of them.
- The mount pans about Z. The head tilts about X at the pivot.
- The master collection is excluded from every view layer.

**Materials:**
- `MAT_BLACK_ALUMINIUM`: #191919, metallic 0.15, roughness 0.38, with a subtle micro-texture.
- `MAT_REFLECTOR_ALUMINIUM`: metallic 1, roughness 0.16.
- `MAT_COB_PHOSPHOR`: yellow phosphor. When on, it emits only to camera and glossy rays, so the visible emitter never double-counts the spot light.

### Accuracy findings (open)

- **Silhouette match against the official photograph:** IoU 0.76 (`deliverables/GLISS_PRODUCT_OFFICIAL_OVERLAY.png`).
- **Main mismatch:** in the photograph the housing sits further forward of the base than in the model. The stem probably meets the housing nearer its rear, or the pivot geometry differs. This is not corrected, because the photo alone cannot separate pivot position from pose.
- **Storyboard sheet vs photograph:** the sheet's base (Ø90 × 25 mm) contradicts the photograph. The photo shows a drum about 1.07 × the housing diameter and 0.55 × it deep. The photograph was followed, as the higher-priority source.
- **Not modelled:** internal hinge mechanism, articulation limits, logos, exposed wiring, cooling fins, rail.

## Scenes and collections

| Scene | Contents |
|---|---|
| `SCENE_PRODUCT_STUDIO` | `04_PRODUCT_STUDIO`: product instance, charcoal-to-walnut sweep, key softbox, champagne rim strip, neutral fill. Also a macro card switched on for shot 2 only. Shots 1, 2 and 10. |
| `SCENE_ARCHITECTURE` | `02_ARCHITECTURAL_ENVIRONMENT`, `03_INSTALLED_GLISS`, `05_CAST_PREVIS`, `06_CINEMATIC_CAMERAS`, `07_AMBIENT_LIGHT_RIG`. Shots 3–9. Two view layers: **BEAUTY** (cast excluded, for final plates) and **PREVIS** (cast visible, for the animatic). |
| `SCENE_WALKTHROUGH_PREVIEW` | Shares the room and ambient-light collections. Has its own Gliss pair (`09_WALKTHROUGH_GLISS`, always on) and no cast. |
| `SCENE_MASTER_EDIT` | VSE with 10 scene strips, each with its camera override. Exactly 360 frames, with markers at the brief's frames. |

All scenes use master frame numbers: shot N is frames f0–f1 of its own scene.

**Room** (origin at the centre of the feature wall, on the floor):
- **Shell:** 7 × 6 × 3.1 m.
- **Feature wall:** honed travertine in 1200 × 600 mm slabs with 3 mm joints.
- **Joinery:** walnut, with shelf LEDs.
- **Floor:** dark oak planks, 180 × 1800 mm, staggered.
- **Glazing:** floor-to-ceiling on x = −3.5, with bronze mullions.
- **Exterior:** a constant blue-hour sky, 34 towers 220–600 m out with randomised lit windows (1.5 m bays, mullion and spandrel gaps), and a low-rise city plane 40 m below with sparse street-level lights.
- **Furniture:** sofa 2700 × 950 × 800 mm, long axis along Y. Round walnut table, Ø900 × 350 mm.
- **Props:** books, ceramics, flowers, greenery, candle, floor lamp.
- **Artwork:** 1800 × 1200 mm, centred at (0, 0.04, 1.65), in a 35 mm walnut frame.

## Lighting

**Installed fixtures:**
- Mounted at (±0.725, 0.95, 3.10), with bases flush to the ceiling.
- Each is aimed by solving pan and tilt so the optical axis through the emitter hits its target at (±0.45, 0.04, 1.65). QA measures the miss distance as 0.0 mm.
- The resulting pose is about 33° tilt. It is provisional until real articulation limits are known.

**Photometry (preview assumptions, not Polycab data):**
- 3000 K, 36° beam with 0.35 blend.
- Light output is set by the `light_output_w` property, currently 70 W radiant, chosen to read clearly in previews.
- The 7 W in the brief is electrical input and is **not** used as Cycles power.
- There is no IES file. One should replace the spot when supplied.

**Switching:**
- Each spot's energy is `on × light_output_w`. The head instance's `cob_on` property drives the COB emission through an Instancer attribute.
- Both use constant keys. The architecture fixtures are off for frames 1–84 and on from 85. The studio product is off until frame 277.

**Ambient light** (constant through the switch-on):
- two 3000 K downlights over the seating;
- a 2700 K floor lamp;
- the joinery shelf LEDs;
- a candle;
- the blue-hour sky through a window portal.

**Colour management:** AgX, Medium High Contrast, exposure 0, gamma 1, no white balance. Identical before and after; QA confirms only the Gliss lights and COBs change between frames 84 and 85.

## Cameras (`06_CINEMATIC_CAMERAS`)

Each camera is a rig: `<ID>_DOLLY` (keyed location, eased Bézier) → `<ID>_ROLL` (Track To `<ID>_TARGET`) → camera.
- Roll stays 0, the approved state; it is the camera's local Z rotation.
- Sensor is 36 mm, horizontal fit.
- Shots switch on timeline markers.

| Shot | Frames | Lens | Notes |
|---|---|---|---|
| CAM_01_PRODUCT_HERO | 1–36 | 85 mm f/5.6 | 12° eased arc around the housing centre. Distance set for about 65 % frame occupancy. |
| CAM_02_COB_MACRO | 37–60 | 100 mm f/8 | Push in along the optical axis toward the COB by 0.12 × housing diameter (7.2 mm) |
| CAM_03_AMBIENT | 61–84 | 35 mm f/5.6 | Static, at (0, 3.6, 1.75), aimed at (0, 0.04, 1.95) |
| CAM_04_TRANSFORMATION | 85–108 | — | **Is** CAM_03: shared camera data and an identity parent transform. QA confirms it is identical. |
| CAM_05_WEDDING_MEMORY | 109–132 | 85 mm f/5.6 | Pushes from y 2.9 to 2.65 on the artwork |
| CAM_06_MATCH_CUT | 133–168 | 85 mm f/4 | (0, 5.05 → 5.00, 1.55), aimed at the couple at (0, 2.0, 1.55) |
| CAM_07_HUMAN_CONNECTION | 169–204 | 85 mm f/4 | (0.55, 3.35 → 3.30, 1.62), aimed at Isha's near eye |
| CAM_08_INSTALLED_GLISS | 205–228 | 70 mm f/5.6 | 8° arc about the right fixture's axis, 0.40 m below the ceiling and about 0.9 m from the fixture |
| CAM_09_ARCHITECTURAL_REVEAL | 229–276 | 24 mm f/8 | The brief's five keyframes, 2.15 m of travel |
| CAM_10_FINAL_PACKSHOT | 277–360 | 85 mm f/8 | Static. The whole fixture fills about 68 % of frame height, centred vertically on the left third; negative space on the right for the END_01 logo. |
| CAM_WALKTHROUGH | 1–240 (own scene) | 24 mm f/8 | The brief's path, re-timed by arc length (keys at 1, 57, 137, 207, 240) |

**Where the build departs from the brief's literal values:**
1. **Cast positions swapped:** Isha is at x +0.3 and Veer at −0.3. The cameras look toward −Y, so +X is screen-left. The proposed blocking (Isha −0.3) would have broken the brief's own rule of "Isha screen left", and the wedding photograph also has her on the left.
2. **Cast visibility:** the cast proxies are hidden in shots 3–5, because standing at y = 2.0 they would block CAM_05's push onto the photograph. They are visible in shots 6–9.
3. **Walkthrough timing:** the keys are re-timed by arc length, as the brief's spline rule requires. Speed still varies between segments; mid-path variation is 0.53 because the Bézier segments ease. A constant-speed path constraint would remove this.

**QA results:**
- Clearance: at least 0.40 m in every architecture shot. The walkthrough stays at least 0.70 m clear (the target is 0.35 m).
- No roll.
- Lenses are constant within each shot and match the brief.
- CAM_08 keeps the fixture in frame throughout. The CAM_09 end frame shows both fixtures and the artwork.

## Cast (`05_CAST_PREVIS`)

`ISHA_01_PROXY` (1.65 m) and `VEER_01_PROXY` (1.80 m) are scaled blocking proxies only:
- They do **not** represent the approved faces or performances.
- There is no collar-gesture animation.
- They are excluded from the BEAUTY layer.
- The final characters come from the approved Seedance or photoreal layers, composited camera-matched.

The match-cut overlay guides (faces, collar, hand) are **not built**. They need the approved character images.

## Missing assets and unresolved issues

| Item | Impact |
|---|---|
| Manufacturer CAD or dimensioned drawing | Product stays PROVISIONAL. The model cannot be certified. |
| IES file, beam angle, lumens | Beam and output are artistic preview values |
| Articulation limits | Installed pan and tilt are unverified |
| Approved ART_WEDDING_01 photograph | The artwork is an animatic placeholder: a 176 × 117 px monochrome crop of the storyboard, upscaled. It must be replaced before any final render. |
| Approved Isha and Veer character sheets and performances | Shots 6–9 have proxies only. No match-cut validation is possible. |
| Official Polycab logo, END_01 layout, typography | None rendered or drawn. Frames 277–360 leave negative space on the right. |
| Catalogue PDF "30MB digital PDF (1)(1).pdf" | Not supplied |
| Natural White 4000 K and Cool White 6500 K listings | Not confirmed against the manufacturer |

## Render time (this machine)

| Render | Time |
|---|---|
| Preview, 960 × 540 at 16 samples | about 4 s per studio frame, about 15 s per room frame |
| Previews as actually rendered | animatic (360 frames) finished 04:21 UTC; walkthrough (240 frames) took about 63 min, finished 05:24 UTC |
| Inspection stills, 1920 × 1080 at 48 samples (measured) | packshot 49 s, COB macro 155 s, room frames 84, 85 and 276 about 177–189 s each |
| Final settings (3840 × 2160, 256 samples, adaptive 0.01, 12 bounces, EXR plus passes) | estimated 30–60 min per frame, so **1–2 weeks** for 360 frames on 4 CPU cores |

A GPU render node, or reduced samples, is recommended for the final.

## Commands

```bash
blender -b --factory-startup --python scripts/build_gliss.py            # rebuild the .blend
blender -b scenes/POLYCAB_GLISS_MASTER.blend --python scripts/qa_gliss.py   # QA + register + camera paths
blender -b scenes/POLYCAB_GLISS_MASTER.blend --python scripts/render_validation.py -- <official.png> <dir>
python3 scripts/compose_validation.py <dir> <official.png>                 # overlay + ortho sheets
python3 scripts/plan_png.py                                                # camera path plan
setsid nohup scripts/render_previews.sh > previews.log 2>&1 &              # animatic + walkthrough
scripts/render_stills.sh                                                   # inspection stills
# final (after approval), per scene, EXR multilayer with passes:
blender -b scenes/POLYCAB_GLISS_MASTER.blend --python scripts/render_frames.py -- SCENE_ARCHITECTURE 61-276 3840 256 <dir> exr
```

The official photograph is not stored in the repository. Download it from `https://cms.polycab.com/media/nsxhpxea/lp0802007bkww-img-01.png`.
