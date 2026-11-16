# 3-bedroom residence: Blender reconstruction from the supplied floor plan

An editable Blender scene of the 3-bedroom apartment in `reference/floor_plan.jpg`. It is rebuilt from a pixel trace of the drawing, with Cycles stills and a walkthrough.

**Accuracy:** the drawing is a 1600 × 839 px marketing JPEG at about 46 px per metre. The model matches it to about ±5 cm. It is **not construction-grade**: no CAD, BIM or dimensioned drawings were supplied.

Built and rendered in Blender 5.2.3 (the brief allows "4.x or a compatible newer release").

## Deliverables

| Brief | File |
|---|---|
| residence_master.blend | `scenes/residence_master.blend` |
| build_residence.py | `scripts/build_residence.py`, which reads the trace in `scripts/plan_trace.py` |
| architectural_validation.json | `metadata/architectural_validation.json` |
| floorplan_comparison.png | `deliverables/floorplan_comparison.png` |
| apartment_isometric_4k.png | `deliverables/apartment_isometric_4k.png` |
| living_room_4k.png … bedroom_02_4k.png | `deliverables/*_4k.png` |
| walkthrough_camera_paths.blend | `scenes/walkthrough_camera_paths.blend` (paths, walk cameras and look targets only) |
| walkthrough_render_sequence/ | `deliverables/walkthrough_render_sequence/frame_0001.png` …, encoded to `deliverables/walkthrough.mp4` |
| top-down validation render | `deliverables/topdown_validation_1488p.png` |

## How the plan was reconstructed

1. **Scale.** The plan carries no scale bar, so the scale is a least-squares fit over 19 dimensioned room spans from the schedule: **46.23 px/m**.
   - Mean error is 0.049 m.
   - One span is outside 0.10 m: the utility width (3.35 m traced against 3.52 m scheduled). Its west face is a structural wall drawn at full thickness, so the schedule figure probably runs to a different face.
2. **Origin and north.**
   - The origin is the inside south-west corner of the master bedroom.
   - Plan-up is +Y, so the drawing's orientation is kept.
   - True north is 17.1° clockwise of plan-up, measured from the needle on the drawing. The `NORTH_Arrow` empty and the sun use it.
3. **Walls.** Every wall is traced from the drawing in pixel coordinates; nothing is inferred from room sizes.
   - Solid-black structural walls and the south-east column keep their drawn thickness.
   - Exterior walls use the provisional 0.23 m thickness, measured outward from the traced room-side face.
   - Interior partitions use the provisional 0.115 m thickness, centred on the traced line.
   - Thickness, height, sills, heads and door heights are all set in `PARAMS` in `plan_trace.py`. Changing one and re-running the build regenerates the model.
4. **Openings** are cut as mesh topology, with no Booleans: each wall is built as solid pieces around its doors and windows.
   - Windows are double glazed (6 mm + 12 mm cavity + 6 mm, IOR 1.52) with charcoal frames and quartz sills.
   - The bedroom windows also get the 0.40 m external ledge and glass guard that the "× 0.40M" labels describe.
5. **Rooms.**
   - Floors and ceilings are built per room from the traced room outlines.
   - Skirting is generated wherever a dry room's edge runs along a wall, with gaps at the doors.
   - Doors have walnut linings, leaves hinged where the drawing's door arcs put them, and bronze levers.
6. **Furniture** is procedural and real-world sized, placed where the drawing shows it:
   - the curved bouclé sofa, nested coffee tables, armchairs and plants;
   - the dining table with six chairs, beds with nightstands and lamps, wardrobes and TV walls;
   - kitchen runs with a tall oven and fridge, the washer-dryer, WCs, vanities and showers.

   No licensed assets were available, so everything is a clean placeholder you can swap in place. Each item is a separate named object.

## Collections

- **Architecture:** `ARCH_Exterior_Walls`, `ARCH_Interior_Walls`, `ARCH_Floors`, `ARCH_Ceilings`, `ARCH_Doors`, `ARCH_Windows`, `ARCH_Columns`, `ARCH_Skirting`.
- **Rooms:** `ROOM_Living`, `ROOM_Dining`, `ROOM_Master`, `ROOM_Bedroom_01`, `ROOM_Bedroom_02`, `ROOM_Kitchen`, `ROOM_Utility`, `ROOM_Bathrooms`.
- **Lights and cameras:** `LIGHTS_Daylight`, `LIGHTS_Interior`, `CAMERAS_Still`, `CAMERAS_Animation`, `REFERENCE_FloorPlan`.
- **Context, added for the views and not part of the apartment:**
  - `CONTEXT_Core` holds the lift lobby, the lifts and the foyer.
  - `CONTEXT_City` holds the ground about 60 m below and generic block towers.

## Materials

All materials are node-based Principled BSDF with procedural texture and bump, so there are no external textures:

- `MAT_Warm_Oak` (staggered planks)
- `MAT_Walnut`
- `MAT_Ivory_Plaster`
- `MAT_Travertine` (1.2 × 0.6 m tiles, banded veining)
- `MAT_Greige_Stone` (600 mm tiles)
- `MAT_Brushed_Bronze` (anisotropic)
- `MAT_Linen`
- `MAT_Boucle`
- `MAT_Clear_Glass`
- `MAT_Ceramic_White`
- `MAT_Quartz`
- `MAT_Warm_Metal`

A few supporting finishes, such as the frame charcoal, rug wool and foliage, are separate materials.

## Lighting

- **Daylight:** a Cycles sun plus a physically based sky.
  - Provisional site: Mumbai (19.02° N), the key plan's "Gokhale Road South".
  - Provisional time: 20 January at 15:30. The sun is at azimuth 227° and elevation 34°.
  - The sun is rotated through the drawing's north angle, so it enters the west and south windows.
  - Every window has a Cycles light portal.
  - The window glass lets shadow and diffuse rays through, so sun and sky reach the rooms without caustics.
- **Interior:** 3000 K recessed downlights on a grid in every room, bedside and floor lamps, a dining pendant and kitchen under-cabinet strips.
- **Exposure:** AgX (Base Contrast), with exposure +0.3 for interiors. Windows are allowed to roll off rather than clip.
- **HDRI:** none. No licensed HDRI was supplied; the procedural sky is used instead.

## Cameras

| Camera | Spec |
|---|---|
| `CAM_01_Isometric` | orthographic; ceilings and the city hidden; walls cut at 2.40 m by `CUTAWAY` Boolean modifiers that are off by default |
| `CAM_02_Entry` | 24 mm at 1.55 m, just inside the door |
| `CAM_03_Living` | 24 mm at 1.50 m |
| `CAM_04_Dining` | 28 mm at 1.50 m, from the living room |
| `CAM_05_Kitchen` | 24 mm at 1.55 m |
| `CAM_06_Master` | 28 mm at 1.50 m |
| `CAM_07_Bedroom1` | 28 mm at 1.50 m |
| `CAM_08_Bedroom2` | 24 mm at 1.50 m |
| `CAM_00_TopDown_Validation` | orthographic, straight down |

## Walkthrough (24 fps, 1488 frames, 62.0 s)

Four Bezier paths, each with its own camera (Follow Path constraint plus Track To a keyed look-target empty), cut together by bound timeline markers:

| Path | Frames | Route |
|---|---|---|
| A | 1–811 | entry, along the dining table, living-room reveal (pause), passage, through the master door, master bedroom (pause) |
| B | 812–1044 | dining into the kitchen |
| C | 1045–1263 | living into bedroom 2 |
| D | 1264–1488 | passage into bedroom 1 |

- Moves ease in and out at a cruise of about 0.41 m/s, peaking at 0.62 m/s, which stays within the brief's 0.35–0.65 m/s range.
- Each path holds for 1–2.5 s at its room reveals.
- Validation checks every frame for clearance, wall crossing and speed.

## Validation

`scripts/validate.py` passes all 10 checks. See `metadata/architectural_validation.json` for the numbers.

| # | Check | Result |
|---|---|---|
| 1 | Footprint vs drawing | 99.4% of the drawing's solid wall fills lie within 3 px of a modelled wall. Room outlines total 123.3 m² against 120.6 m² in the schedule (+2.3%). |
| 2 | Room dimensions | 18 of 19 spans are within 0.10 m. The exception is the utility width (−0.17 m), explained above. |
| 3 | Adjacency | All 14 expected door and open-plan links are confirmed in the model. |
| 4 | Entrance and corridors | Every room is reachable from the entry. Door clear widths are at least 0.75 m to habitable rooms and at least 0.60 m to bathrooms. |
| 5 | Intersections | No furniture-to-architecture or furniture-to-furniture overlaps across 250 furniture meshes, and no wall crosses another wall's opening. |
| 6 | Door swings | A full 90° sweep of all 11 leaves is clear of furniture. |
| 7 | Windows | All 6 openings sit within the drawn glazing lines. |
| 8 | Cameras | Every still and every walkthrough frame is at least 0.20 m from geometry. No path step crosses geometry, and peak speed is 0.62 m/s. |
| 9 | Orientation | The north arrow is at 17.13°, as on the drawing; the plan is not mirrored. |
| 10 | Top-down render | Rendered; it is used for `floorplan_comparison.png`. |

The assumptions and gaps on the drawing are listed in the JSON under `assumptions`:
- Wall thicknesses and heights are not dimensioned.
- The bedroom 2 depth is 4.17 m as drawn, against 3.87 m in the schedule (probably excluding the wardrobe zone).
- The powder-room and bathroom 2 door hinges are interpretations.
- There is no ceiling plan.
- The site and sun time are provisional.

## Render settings and where they differ from the brief

The renders ran on a 4-core CPU with no GPU, so two settings are lower than the brief:

| | Brief | Rendered | Full-spec command |
|---|---|---|---|
| Stills | 3840 × 2160, 256–512 samples | 3840 × 2160, 96 samples (adaptive, OpenImageDenoise), 16-bit PNG | `render_stills.py -- all 3840 384 deliverables` (add `exr` for OpenEXR) |
| Walkthrough | 3840 × 2160 | 480 × 270 preview sequence, 6 samples, denoised | `render_walkthrough.py -- 1 1488 3840 128` |

Motion blur is off: it is subtle at walking speed, and a preview resolution would only smear it.

The 4K stills are 16-bit PNGs of about 35–40 MB each.

## Rebuild

```bash
blender -b --factory-startup --python scripts/build_residence.py
```

```bash
blender -b scenes/residence_master.blend --python scripts/render_stills.py -- CAM_00_TopDown_Validation 2400 32 deliverables
```

```bash
blender -b scenes/residence_master.blend --python scripts/validate.py -- deliverables/topdown_validation_1488p.png
```

```bash
blender -b scenes/residence_master.blend --python scripts/render_stills.py -- all 3840 96 deliverables
```

```bash
blender -b scenes/residence_master.blend --python scripts/render_walkthrough.py -- 1 1488 480 6
```

```bash
scripts/encode_walkthrough.sh
```
