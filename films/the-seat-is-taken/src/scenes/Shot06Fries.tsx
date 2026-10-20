// SHOT 06 · THE FRIES — close-up of Penny's hand taking one fry, then Leonard's look: Penny → Sheldon.
import React from 'react';
import { World } from '../components/World';
import { Stamp } from '../components/Type';
import { kf, leonard, pennySeated, held, Fry, chew } from './common';
import { C, CUES, SHOTS } from '../config';

export const Shot06Fries: React.FC<{ f: number }> = ({ f }) => {
  const reaction = f >= 334;
  const cam = reaction ? { cx: 1075, cy: 470, z: 2.0 } : { cx: 985, cy: 668, z: kf(f, [[318, 3.1], [334, 3.3]]) };
  // reach in (318–326), pinch (326–329), lift out (329–334), then eat
  const reach = kf(f, [[318, 0], [326, 1], [329, 1], [334, .45]]);
  const toMouth = reaction ? kf(f, [[334, 0], [338, 1]]) : 0;
  const armL = { sh: reaction ? -30 * toMouth + 14 : 14 + 46 * reach, el: reaction ? -40 - 115 * toMouth : -40 + 40 * reach, hand: (f >= 326 ? 'fist' : 'open') as any };
  const hasFry = f >= 327 && f < 341;
  const penny = pennySeated(f, {
    lean: reaction ? 0 : -9 * reach,
    face: { turn: -.35, eyeX: reaction ? 0 : -.8, eyeY: reaction ? 0 : .7, smile: .35, mouth: reaction && f > 338 ? chew(f, true) : 0 },
    armL, holdL: hasFry ? held(armL, <Fry x={0} y={-6} rot={reaction ? 0 : 20} s={.9} />, 0) : undefined,
  });
  const leo = leonard(f, {
    fries: f >= 327 ? 6 : 7,
    face: reaction ? { turn: kf(f, [[334, .4], [339, .4], [341, .7]]), eyeX: 1, eyeY: kf(f, [[334, .2], [339, .2], [341, -.6]]), brow: kf(f, [[334, .1], [338, .55]]), mouth: 0 } : { eyeX: .2, eyeY: .6 },
  });
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, squash: [0, 0, .6], penny, leonard: leo }} />
      <Stamp x={960} y={110} text="Takes the fries" at={CUES.fries} until={SHOTS.fries[1]} color={C.red} size={70} />
    </>
  );
};
