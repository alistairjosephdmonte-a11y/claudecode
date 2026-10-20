// SHOT 05 · PENNY ARRIVES — she walks in, sits on the free cushion without hesitation; quick reaction from Sheldon.
import React from 'react';
import { World } from '../components/World';
import { Caption } from '../components/Type';
import { kf, leonard, lip, sheldonStand, pennySeated } from './common';
import { PENNY_SEAT } from '../components/World';
import { C, CUES, SHOTS } from '../config';

export const Shot05Penny: React.FC<{ f: number }> = ({ f }) => {
  const reaction = f >= 308;
  const cam = reaction ? { cx: 1420, cy: 365, z: 2.6 } : { cx: kf(f, [[272, 1230], [306, 1170]]), cy: 520, z: kf(f, [[272, 1.42], [306, 1.5]]) };
  const sit = kf(f, [[282, 0], [292, 1]]);
  const walking = f < 282;
  const penny = {
    ...pennySeated(f, { face: { turn: kf(f, [[272, -.5], [290, -.2]]), eyeX: kf(f, [[272, -1], [284, -.6], [300, -.3]]), eyeY: kf(f, [[272, .6], [284, .2]]), smile: kf(f, [[278, .2], [286, .65]]), mouth: lip('penny1', f) } }),
    x: kf(f, [[272, 1690], [282, PENNY_SEAT.x]]), y: kf(f, [[272, 935], [282, 935], [292, PENNY_SEAT.y]]),
    sit, walk: walking ? f * .6 : 0, bob: walking ? Math.abs(Math.sin(f * .6)) * 6 : -6 * Math.sin(Math.PI * Math.min(1, Math.max(0, (f - 290) / 6))),
  };
  const squash = [0, 0, kf(f, [[288, 0], [292, 1], [296, .6]])];
  const sh = sheldonStand(f, { face: reaction ? { turn: -.65, eyeX: -1, eyeY: .55, brow: kf(f, [[308, .2], [312, .65]]), lids: 0 } : { turn: -.4, eyeX: -1, eyeY: .3 } });
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, squash, sheldon: sh, penny, leonard: leonard(f, { eat: !reaction && f < 284, face: { eyeX: 1, turn: .3 } }) }} />
      {!reaction && <Caption x={150} y={150} name="Penny" until={SHOTS.penny[1]} phrases={[{ at: CUES.comfy, tokens: [{ t: 'Looks comfy' }, { t: '.', c: C.gold }] }]} />}
    </>
  );
};
