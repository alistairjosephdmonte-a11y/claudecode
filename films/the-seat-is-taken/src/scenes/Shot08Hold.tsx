// SHOT 08 · THE HOLD — the three of them on the couch. Penny eats, Leonard sags, Sheldon sits bolt upright in his spot.
import React from 'react';
import { World, SPOT_SEAT } from '../components/World';
import { Title } from '../components/Type';
import { kf, leonard, pennySeated, held, chew } from './common';
import { Fries } from '../components/Set';
import { CUES } from '../config';

export const Shot08Hold: React.FC<{ f: number }> = ({ f }) => {
  const cam = { cx: 960, cy: kf(f, [[420, 600], [450, 592]]), z: kf(f, [[420, 1.22], [450, 1.28]]) };
  const eat = Math.max(0, Math.sin((f - 420) * .3));
  const armR = { sh: -10, el: 60, hand: 'hold' as const };
  const penny = pennySeated(f, {
    face: { turn: 0, eyeX: 0, smile: .4, mouth: chew(f, true) },
    armR, holdR: held(armR, <Fries x={0} y={22} s={.8} count={5} />),
    armL: { sh: 14 - 30 * eat, el: -40 - 110 * eat, hand: 'fist' },
  });
  const leo = { ...leonard(f, { bob: -10, face: { lids: .45, sad: .7, eyeX: 0, eyeY: .4, mouth: 0 } }), holdR: undefined, armR: { sh: -6, el: 10, hand: 'open' as const } };
  const sheldon = { ...SPOT_SEAT, sit: 1, face: { eyeX: 0, eyeY: 0, brow: .1, frown: .2, lids: 0 }, armL: { sh: 4, el: -25, hand: 'fist' as const }, armR: { sh: -4, el: 25, hand: 'fist' as const } };
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 0, foodOnSpot: false, foodOnTable: true, squash: [.4, .3, .6], sheldon, leonard: leo, penny }} />
      <Title at={CUES.title} />
    </>
  );
};
