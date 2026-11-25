# Mousetrap chain-reaction physics test

A Blender rigid-body test: a floor laid with 308 set mousetraps, a rubber ball dropped into the field, and ping-pong balls resting on some trap pedals. Every snap is simulated. Nothing is hand-animated, so the cascade is whatever the physics produces.

Inspired by the trap-floor gag in a 1997 film clip supplied as a reference. The set, props, camera and lighting are original.

## Result

- 308 traps, 38 ping-pong balls and one rubber ball.
- 252 of the 308 traps fire. The first fires on frame 29, when the ball lands, and the last on frame 205.
- The film is 264 frames at 24 fps (11 s) and runs at 0.5× slow motion.
- Rendered in Cycles at 960 × 540 with 16 samples and OpenImageDenoise.
- Output is `deliverables/trap_chain_test.mp4`. The frames are in `deliverables/frames/`.

## How a trap works in the sim

Each trap is two rigid bodies plus three constraints:

| Part | Detail |
|---|---|
| Base | Pine board, 98 × 45 × 8 mm, 16 g. The pedal, coils and stamp are visual children with no collision. |
| Spring bar | U wire, 40 × 40 mm, 7 g. |
| `Hinge` | Pivots the bar across the board, limited to the half-turn from set to sprung. |
| `Latch` (FIXED) | Holds the bar in the set position until the trap fires. |
| `Motor` | When the trap fires, drives the bar at about −400 rad/s (±15% per trap). Its reaction kicks the base 4–6 cm into the air, and the base flips. |

Bullet can't fire a constraint on contact, so `build_sim.py` steps the simulation one frame at a time and detects firing events itself. A trap fires when any of these happens:

- a moving body enters the 20 mm zone above its top face;
- it is tilted more than 8°;
- it is shoved more than 4 mm.

The script then keys the latch off and the motor on for the next frame. Once the run finishes, the motion is baked to plain keyframes and the rigid-body world is removed. `scenes/trap_chain.blend` therefore plays back and renders without any cache.

## Settings

| | Value |
|---|---|
| Time scale | 0.5 (slow motion) |
| Substeps per frame | 50 |
| Solver iterations | 30 (40 on trap constraints) |
| Collision margin | 0.5 mm |
| Trap pitch | 122 × 70 mm, with small jitter and twist. Traps that overlap at spawn pop apart and fire falsely on frame 2. |

The trap count, the frame count and every physics constant are at the top of `scripts/build_sim.py`.

## Rebuild

Build, simulate, bake and grade, saving to `scenes/`. This takes about 7 minutes on 4 CPU cores.

```bash
blender -b --factory-startup --python scripts/build_sim.py -- 16 20 360 scenes/trap_chain.blend
```

Render frames 1–264. This takes about 10 s per frame.

```bash
blender -b scenes/trap_chain.blend --python scripts/render_frames.py -- 1 264 960 16
```

Encode the frames to the MP4.

```bash
scripts/encode.sh
```
