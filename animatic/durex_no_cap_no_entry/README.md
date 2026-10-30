# DUREX: NO CAP, NO ENTRY — 30-second Blender animatic

Deadpan Indian absurdist fashion comedy. A young man in a royal-blue cap gets into a mysterious
Mumbai underground club whose only dress code is "wear a cap". The brand appears only in the final
2 seconds (frames 673–720), and only as **labelled placeholders** until approved assets are supplied.

> **Status: blocking animatic, not final picture.** Characters and sets are procedural primitive
> blockout geometry. Nothing here is photoreal. Look development needs approved reference sheets,
> real character/wardrobe assets and the approved brand plates. See [Limitations](#limitations).

## Deliverables

| Item | Path |
|---|---|
| Blender project (Blender 4.2 LTS, EEVEE Next), scenes `DUREX_MAIN`, `END_CARD`, `EDIT_VSE` | `DUREX_NO_CAP_animatic.blend` |
| 30 s animatic MP4, 1920×1080, 24 fps, H.264, 720 frames, no audio | `output/DUREX_NO_CAP_animatic_30s.mp4` |
| Full-resolution 1920×1080 EEVEE stills (one per shot + end card) | `output/stills_1080p/` |
| Contact sheet of the animatic | `output/contact_sheet.png` |
| Automated QC report (all 720 frames) | `qc/qc_report.md`, `qc/qc_report.json` |
| Reproducible build scripts (bpy only, no external assets) | `scripts/` |

### Reproduce

```bash
blender -b --factory-startup --python scripts/build_scene.py
```

```bash
blender -b DUREX_NO_CAP_animatic.blend --python scripts/qc.py
```

```bash
blender -b DUREX_NO_CAP_animatic.blend --python scripts/render_shots.py -- --pass eevee_50 --engine EEVEE --pct 50 --samples 8
```

```bash
blender -b DUREX_NO_CAP_animatic.blend --python scripts/assemble_vse.py -- --pass eevee_50 --out output/DUREX_NO_CAP_animatic_30s.mp4
```

For a native 1080p render, use `--pass eevee_100 --pct 100 --samples 16` and assemble from that pass.
On a GPU workstation that takes minutes. In this CPU-only container it takes about 43 s per frame.

| Script | Builds |
|---|---|
| `common.py` | Shot table, colour/HEX helpers, mesh primitives, node materials, action/NLA writers |
| `environment.py` | Street, facade, doorway, stanchions, rope, shelf, corridor and curtain, club interior, all lights |
| `cap_asset.py` | The single hero-cap mesh: 6-panel crown with seam grooves and stitch rows, top button, 6 eyelets, curved brim, rear arch, strap and buckle, twill material |
| `cast.py` | Cast sheet, armature rigs, bone-parented body and wardrobe meshes, face controls, IK |
| `cartoon.py` | Cel traffic cone, satellite dish (bend-deform sag), elephant with cel version of the cap |
| `perform.py` | Distance-locked gait solver, per-shot performances, NLA baking, foot-lock IK, props, cameras |
| `endcard.py` | `END_CARD` scene with placeholders and the campaign line |
| `render_shots.py` / `assemble_vse.py` | Per-shot renders, then VSE edit and MP4 export |
| `qc.py` / `render_stills.py` | Automated checks, QC stills |

## Scene organisation

* **Collections:** `LOCATION_EXTERIOR`, `LOCATION_INTERIOR`, `CHARACTERS` (one sub-collection per
  character plus `RIG_CONTROLS`), `CAPS`, `CARTOON_ELEMENTS`, `LIGHTING`, `CAMERAS`, `PROPS`.
* **Cameras:** `CAM_01` to `CAM_10`, one per shot, each with its own action (`CAM_xx_SHxx`) and
  focus-distance action. Timeline markers `SH01`–`SH10` bind each camera to its shot.
* **Animation:** every character has one action per shot (e.g. `HERO_01_SH05`, `BOUNCER_01_SH07`),
  laid out as sequential NLA strips on a `<RIG>_SHOTS` track. Shot-specific prop actions:
  `VELVET_ROPE_SH07_SH09`, `GIFT_CAP_SH09`, `HERO_01_CAP_TUG_SH05`, `GUEST_02_CONE_WOBBLE_SH03`,
  `GUEST_03_DISH_SAG_SH04`, `CARTOON_ELEPHANT_01_EAR_SH08`.
* **Rig controls (simple):** armature per character with root, spine, neck, head, eye and brow
  bones, 3-bone arms and legs.
  * Hand IK constraints (`IK_R_BRIM`, `IK_R_ROPE`, `IK_R_CAP`, `IK_L/R_CAP`) target `CTRL_*` empties.
    Those empties are parented to the prop being touched, or keyed from the evaluated prop, so fingertips meet the object.
  * Leg IK (`IK_FOOTLOCK_L/R`) pins planted feet.
* **Edit:** scene `EDIT_VSE` holds one image strip per rendered shot, plus `SH10_ENDCARD` at frame 673. Hard cuts only, no transitions or overlays.

## Geography and continuity

```
                 N (+Y)   club interior y 5..18 (bar on north wall, elephant at bar)
                 |        corridor y 0.35..5, black velvet curtain at y 4.7
   facade y=0 ===|==[ DOOR x -0.6..0.6 ]==== shelf (x 1.3, z 1.28)
                 |   o------rope------o           o BOUNCER mark (0.95,-0.95), faces screen-left
                 |  stanchion L      stanchion R
  queue -> -> -> STOP (-0.25,-1.55)          (entrance-left = screen-left)
  (y -1.85, x -1.1 .. -3.95, all face screen-right)
   pavement y -3..0  |  curb  |  wet road y < -3        CAMERA SIDE = SOUTH
```

* All exterior story cameras sit south of the guest/bouncer line, so the 180° axis is never crossed.
  Movement is left to right toward the door.
* Guests' eyelines go screen-right to the bouncer; the bouncer's go screen-left.
* The bouncer stands at entrance-right. He leaves his mark only once per rope opening: one short step
  toward the entrance-left stanchion to reach the hook (SH07: out and back; SH09: out at the end of the shot).
* The rope is unhooked from the **entrance-left** stanchion and carried **screen-right** toward the
  bouncer's side. It always opens the same way.

## Camera breakdown

| Shot | Frames (TC) | Camera | Lens / f-stop | Move | Action / gag beat (120 BPM, 12 f/beat) |
|---|---|---|---|---|---|
| SH01 | 1–72 (00:00–03:00) | CAM_01 | 24 mm f/4 | Slow low dolly in, 0.55 m high | Establishing: facade, door, bouncer screen-right, rope, queue screen-left (cone and dish visible), HERO_01 in background walking in from left |
| SH02 | 73–144 (03:00–06:00) | CAM_02 | 50 mm f/2.8 | Slight push-in, medium | GUEST_01 approaches; bouncer's arm extends horizontally **f97**; guest stops, looks down f102–122, steps aside and exits left |
| SH03 | 145–216 (06:00–09:00) | CAM_03 | 35 mm f/2.8 | Lateral track screen-right | GUEST_02 with flat cel traffic cone (head occludes its base); one head shake **f169–181**; she turns and exits screen-left; cone wobbles |
| SH04 | 217–288 (09:00–12:00) | CAM_04 | 28 mm f/4 | Low angle, slow creep | GUEST_03 balances a giant cel dish that bows under its weight; left eyebrow raise **f253**; point away **f265** |
| SH05 | 289–360 (12:00–15:00) | CAM_05 | 50 mm f/2.8 | Chest-height track with the hero | HERO_01 walks in calmly, stops **f337**, weight shift, right hand on brim **f349** (contact verified), small tug |
| SH06 | 361–432 (15:00–18:00) | CAM_06 | 85 mm f/2 | Alternating CUs (cuts inside the shot at f385 and f409, constant keys) | Bouncer looks up at the cap, eyes trace the brim / hero CU, expressionless / bouncer returns gaze, one tiny nod **f421** |
| SH07 | 433–504 (18:00–21:00) | CAM_07 | 35 mm f/2.8 | Hold, then follow through the doorway | Bouncer steps to the rope and unhooks it from entrance-left **f445**, carries it screen-right back to his mark; hero walks between the stanchions into the magenta-lit corridor; camera ends inside the threshold |
| SH08 | 505–576 (21:00–24:00) | CAM_08 | 24 mm f/4 | Slow push, wide | Six capped clubgoers dancing (grounded feet, asynchronous phase and half-time); flat cel elephant in a blue cap at the bar, casting a contact shadow, partly hidden by the foreground stool; nobody reacts |
| SH09 | 577–648 (24:00–27:00) | CAM_09 | 50 mm f/2.8 | Locked off | GUEST_04 without a cap is blocked (f589); bouncer turns, takes the cap from the shelf (f607), steps in, hands it over **f625**, she puts it on **f637**, he unhooks the rope (f643–648) |
| SH10 | 649–672 (27:00–28:00) | CAM_10 | 85 mm f/2 | Gentle push | Hero inside the club, cap sharp, magenta bokeh |
| SH10b | 673–720 (28:00–30:00) | `END_CARD` scene | ortho graphics layer | Hard cut on the bass stop **f673** | Placeholders for the approved Durex logo and packshot, plus the line "NO COVER. NO ENTRY." (the only on-screen text) |

The shutter is 180° (`motion_blur_shutter 0.5`, position *Start*, so frames never sample across a cut).
Each camera has keyed focus distance on its subject, giving subtle depth of field.

## Cast (fixed identities and wardrobe)

| ID | Height | Look |
|---|---|---|
| HERO_01 | 1.75 m | Indian man, 26, medium-brown skin, natural black hair, oversized worn black leather jacket (open over a charcoal shirt), loose faded denim, black trainers, **hero cap** |
| BOUNCER_01 | 1.90 m, broad | Indian man, 42, deep-brown skin, close-cropped hair, moustache, charcoal suit, white shirt, navy cap |
| GUEST_01 | 1.72 m | Indian man, 25, olive shirt, no cap |
| GUEST_02 | 1.62 m | Indian woman, 27, oversized olive bomber, dark trousers, flat cel traffic cone |
| GUEST_03 | 1.76 m | Indian man, 30, cream patterned shirt, dark trousers, flat cel satellite dish |
| GUEST_04 | 1.60 m | Indian woman, 26, black top, no cap until SH09 |
| CLUB_EXTRA_01–06 | 1.58–1.82 m | Indian adults (21+), assorted tops, 3 blue and 3 navy caps |
| CARTOON_ELEPHANT_01 | ~3 m | Flat two-tone cel elephant with ink outline, wearing the cap asset in cel shading |

## Hero cap

* **One mesh datablock**, `ASSET_HERO_CAP_MESH` (3,556 verts), linked by all 10 cap objects: hero,
  bouncer, gift cap, six extras and the elephant. Topology is identical everywhere. There is no
  morphing; colour changes are object-level material overrides only.
* Modelled features:
  * six-panel crown with seam grooves and twin stitch rows
  * sweatband stitch line and top button
  * six embroidered eyelets
  * curved brim, curving down across its width, with three concentric stitch rows
  * rear arch opening, adjustment strap and buckle
* Material: cotton twill, with diagonal-weave bump normals, sheen and dashed stitch thread.
* **No logo on any cap.**
* **Colour:** `#1F4BA5` is a **placeholder** approximation of Durex royal blue (also stored as a scene
  property). Before the final render, replace it with the HEX sampled from approved brand artwork
  (`MAT_CAP_TWILL_HERO_BLUE` → `cap_base_hex`, and `MAT_CEL_CAP_BLUE`).

## Lighting

* **Exterior:**
  * warm practical bulb over the door (2700 K-ish point light)
  * cool blue neon area fill from camera-left
  * small blue and red neon tubes (no text)
  * sodium street spots and a cool sky bounce
* **Wet surfaces:** puddle masks lower the roughness, so screen-space reflections pick up the blue and red.
* **Interior:**
  * muted magenta overhead areas
  * magenta corridor strips
  * warm bar light
  * cool back rim
  * a low neutral key on the hero, so the cap stays recognisably blue
* All lights are physical point, spot or area lights with inverse-square falloff. EEVEE Next has no bloom; view transform is AgX.

## Sound design guide (markers only — no audio generated)

`EDIT_VSE` carries:

* `BAR_01`–`BAR_15` downbeats for a separately licensed 120 BPM track (12 frames per beat).
* Shot markers.
* `SFX_*` cue markers:
  * street traffic
  * muffled club bass through the door
  * wet-pavement footsteps
  * cone wobble
  * dish creaks
  * rope hook clinks (f445, f645)
  * cap fabric tug and hand-off
  * crowd ambience in the club
  * `SFX_FINAL_BASS_STOP_HARD_CUT` at f673

Major gags land on beats: f97, f169, f253, f265, f337, f349, f421, f445, f625, f637, f673.

## QC summary

`qc/qc_report.md` is generated by `scripts/qc.py`, which evaluates every frame. All checks pass:

* **Runtime and shots:** 720 frames at 24 fps (30.00 s), 1920×1080; 10 shots × 72 frames, each bound to its own camera at the specified lens.
* **Door geography:** the bouncer's head projects screen-right of the door centre in every exterior frame while he is on his mark.
  * He is on his mark (0.0 m deviation) in SH01–06.
  * His only departure is the deliberate 0.61 m rope step in SH07/SH09.
* **180° rule and screen direction:** all exterior cameras stay on the south side of the axis, and every approach moves left to right in world space and on screen.
* **No collisions:**
  * minimum character separation 0.71 m
  * stanchion clearance at least 0.36 m
  * the hero passes between the stanchions with 0.39 m clearance on each side
* **Hand-to-prop contacts:** brim, gift cap (bouncer and guest), rope hook. The maximum fingertip gap is 0.1 mm.
* **Foot sliding:** the most any planted foot moves is 0.6 mm per frame. The gait solver locks the stance foot and leg IK pins every stance.
* **Rope:** opens from entrance-left toward screen-right (end x −0.35 → 0.65).
* **Cartoon elements:** cel objects cast real shadows; the elephant's feet touch the floor (z = −0.009); the foreground stool hides part of the elephant from CAM_08 (ray test).
* **Brand:**
  * no text or brand objects exist in the story scene
  * the logo and packshot placeholders exist only in `END_CARD`
  * the end-card strip starts at f673, the final 2 seconds
  * caps carry no logos
* **Manual review of QC stills:**
  * the cap silhouette and colour hold across shots, including the club key light balanced to stop magenta turning the cap lavender
  * the club interior is hidden from the street by the entry curtain, so the elephant is not revealed early

## Limitations

These are reported as limitations, not hidden.

1. **Blockout only.** Humans are rigid-segment mannequins with simple faces: no finger articulation,
   no blinks, no cloth simulation. The look is not photographic. Final look development needs approved
   character, wardrobe and set assets, plus reference sheets.
2. **Resolution of the animatic.** The container has no GPU (Mesa llvmpipe), so EEVEE runs at about
   18 s per frame at 960×540 and about 43 s at 1080p. The 30 s MP4 is a 1920×1080 file assembled in
   the VSE from **960×540, 8-sample EEVEE renders, scaled ×2**. Native 1920×1080 renders were made
   only for the QC stills in `output/stills_1080p/`. One command reproduces a full native 1080p pass.
3. **Low-res preview pass:** the Workbench playblast was run for SH01–SH04 only. It was stopped to free
   CPU for the EEVEE pass. The other shots were previewed as EEVEE QC stills and covered by the
   all-frame automated QC.
4. **Brand assets are placeholders.** These are neutral grey shapes named
   `PLACEHOLDER__DUREX_LOGO__APPROVED_ASSET_REQUIRED` and
   `PLACEHOLDER__CONDOM_PACKSHOT__APPROVED_ASSET_REQUIRED`. They are deliberately not an imitation
   of the logo or packaging. The campaign line uses Blender's default font; swap in the approved typeface.
5. **Cap colour HEX** is a placeholder (see above).
6. **"Folded" cap (SH09):** to keep one reusable cap asset with matching topology and no morphing, the
   gift cap is the same asset resting on the shelf. It is not folded. A true fold needs a separate,
   approved deformation or asset.
7. **Bouncer's door position:** he steps once toward the stanchion to reach the rope (out and back in
   SH07; out at the end of SH09). The QC report records this.
8. **Turns in place** pivot on pinned feet via leg IK; there are no stepping turns. Guest exits begin with a short pivot.
9. **SH06 alternating close-ups** are cut inside the single CAM_06 shot with constant-interpolated camera keys, to keep one camera per shot.
10. **End-card camera:** `END_CARD` uses an extra orthographic graphics-layer camera (`ENDCARD_LAYER_CAM`). It is not a story camera.
11. **No audio** is included: no generated music, and no SFX library was available. Timing markers are provided instead.
