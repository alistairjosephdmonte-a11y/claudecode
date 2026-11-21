# Contact and occlusion validation

29 checks, 29 pass, 0 fail. Measured on `scenes/OFFBRIEF_S01E01_MASTER.blend`.

| Check | Result | Detail |
|---|---|---|
| BOX_01 soles on the support when grounded | PASS | max |sole - surface| = 0.00 mm over 338 frames |
| Both feet land on the tabletop | PASS | frame 401: z = 0.75 m, table top = 0.75 m |
| Contact shadow present when grounded, absent on screen | PASS | alpha 0.85 on contact, fading with height in the air, 0 while BOX_01 is part of the illustration |
| On-screen BOX_01 sits in front of the display plane | PASS | y = 3.405 m vs display plane y = 3.415 m (BOX_01 occludes the slide, never the reverse) |
| After stepping out, BOX_01 never re-enters the wall/screen plane | PASS | max y after frame 372 = 3.195 m |
| No teleport (per-frame move under 25 cm) | PASS | max per-frame move 23.8 cm |
| BOX_01 clears the water glass | PASS | closest centre distance 0.303 m (needs > 0.126 m) |
| Rig layer order (face over body, gloves/sneakers over limbs) | PASS | face cards 2 mm in front of the body card |
| Shot 06: line of sight camera -> BOX_01 face | PASS | frame 336: clear |
| Shot 07: line of sight camera -> BOX_01 face | PASS | frame 384: clear |
| Shot 08: line of sight camera -> BOX_01 face | PASS | frame 432: clear |
| Shot 09: line of sight camera -> BOX_01 face | PASS | frame 540: clear |
| Shot 10: line of sight camera -> BOX_01 face | PASS | frame 672: clear |
| Shot 01: CAM_MASTER inside room, clear of geometry, north-facing | PASS | pos (-0.3, -3.15, 1.45), nearest surface 0.35 m, forward.y 1.00 |
| Shot 01: 180-degree rule (window-side actors left of client/screen-side actors) | PASS | 4 west/east pairs in frame |
| Shot 02: CAM_SLOANE inside room, clear of geometry, north-facing | PASS | pos (0.4, 0.0, 1.22), nearest surface 0.38 m, forward.y 0.60 |
| Shot 03: CAM_ELLIOT inside room, clear of geometry, north-facing | PASS | pos (0.78, 0.97, 1.5), nearest surface 0.65 m, forward.y 0.95 |
| Shot 04: CAM_SLOANE inside room, clear of geometry, north-facing | PASS | pos (0.45, -1.95, 1.25), nearest surface 0.82 m, forward.y 0.83 |
| Shot 05: CAM_NICO inside room, clear of geometry, north-facing | PASS | pos (0.33, -1.56, 1.22), nearest surface 0.54 m, forward.y 0.65 |
| Shot 06: CAM_BOX inside room, clear of geometry, north-facing | PASS | pos (0.22, 0.95, 1.32), nearest surface 0.52 m, forward.y 0.98 |
| Shot 07: CAM_TRANSITION inside room, clear of geometry, north-facing | PASS | pos (0.85, 0.3, 1.3), nearest surface 0.54 m, forward.y 0.93 |
| Shot 08: CAM_BOX inside room, clear of geometry, north-facing | PASS | pos (0.25, 0.35, 1.02), nearest surface 0.27 m, forward.y 0.99 |
| Shot 09: CAM_MASTER inside room, clear of geometry, north-facing | PASS | pos (-0.2, -2.7, 1.4), nearest surface 0.80 m, forward.y 1.00 |
| Shot 09: 180-degree rule (window-side actors left of client/screen-side actors) | PASS | 2 west/east pairs in frame |
| Shot 10: CAM_SLOANE inside room, clear of geometry, north-facing | PASS | pos (0.3, -0.9, 1.12), nearest surface 0.17 m, forward.y 0.95 |
| NICO_01: no interpenetration with furniture/props | PASS | none |
| SLOANE_01: no interpenetration with furniture/props | PASS | none |
| ELLIOT_01: no interpenetration with furniture/props | PASS | none |
| VANTA_CLIENT: no interpenetration with furniture/props | PASS | none |
