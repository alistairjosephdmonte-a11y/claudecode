# Actor-position continuity report

Sampled 130 frames (every 6th frame plus every shot's first and last frame).

| Actor | Pose | Root position (m) | Max root drift (m) | Max yaw drift (deg) | Pelvis z range (m) | Shoe sole z range (m) | Shots on screen | Result |
|---|---|---|---|---|---|---|---|---|
| NICO_01 | seated | (-1.05, -0.4, 0.0) | 0.000000 | 0.0000 | 0.557-0.557 | 0.005-0.005 | 1, 4, 5, 9 | PASS |
| SLOANE_01 | seated | (-1.05, 1.0, 0.0) | 0.000000 | 0.0000 | 0.549-0.549 | 0.005-0.005 | 1, 2, 4, 9, 10 | PASS |
| ELLIOT_01 | standing | (1.45, 2.85, 0.0) | 0.000000 | 0.0000 | 0.949-0.949 | 0.005-0.005 | 1, 3, 9 | PASS |
| VANTA_CLIENT | seated | (0.95, -0.82, 0.0) | 0.000000 | 0.0000 | 0.564-0.564 | 0.005-0.005 | 1 | PASS |

Nobody stands, walks or changes seats. The client (VANTA_CLIENT) is in frame only where the table above lists it; every other shot, including shot 09 where the client speaks, keeps the client off screen at the same chair.
