# BOX_01 trajectory report

BOX_01 is one continuous flat 2D layered rig (`BOX_01` root, `BOX_01_FACING` yaw, `BOX_01_SQUASH` squash pivot, art cards). It is never swapped, morphed or duplicated. The same object is the on-screen illustration and the tabletop character. Art scale is fixed at 0.4 m per 1000 px, so it keeps the same world size from the screen to the table.

Motion is keyed on the 24 fps timeline with STEPPED modifiers (frame step 2): 12 fps-style holds.

## Phases

| Frames | Phase | Support |
|---|---|---|
| 1-312 | hidden | - |
| 313-360 | screen | - |
| 361-372 | airborne | SIDEBOARD |
| 373-390 | grounded | SIDEBOARD |
| 391-398 | airborne | FLOOR |
| 399-400 | airborne | TABLE |
| 401-720 | grounded | TABLE |

## Key events

- Revealed on the illustration slide at frame 313, 1 cm in front of the display plane (y = 3.405).
- Steps through the screen plane at frames 361-368, drops onto the sideboard top (0.9 m) at frame 372.
- Leaps from the sideboard edge at frame 390 (peak z 1.055 m) and lands on the tabletop at frame 401 at (0.0503, 2.05, 0.75).
- Max speed 5.71 m/s (the leap). Largest single-frame move 23.8 cm. Frames with any move above 6 m/s (a teleport test): none.
- Per-frame positions are in `box01_trajectory.json`.
