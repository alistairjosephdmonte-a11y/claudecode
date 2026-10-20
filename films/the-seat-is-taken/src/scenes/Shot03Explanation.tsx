// SHOT 03 · THE EXPLANATION — medium close-up on Leonard, an open-palm gesture at the food, a short awkward pause.
import React from 'react';
import { World } from '../components/World';
import { Caption } from '../components/Type';
import { kf, leonard, lip, sheldonStand } from './common';
import { C, CUES, SHOTS } from '../config';

export const Shot03Explanation: React.FC<{ f: number }> = ({ f }) => {
  const cam = { cx: kf(f, [[128, 905], [190, 880]]), cy: 525, z: kf(f, [[128, 1.85], [190, 1.95]]) };
  const g = kf(f, [[138, 0], [146, 1], [172, 1], [180, 0]]);
  const leo = leonard(f, {
    face: { turn: kf(f, [[130, -.35], [176, -.35], [182, .35]]), eyeX: kf(f, [[176, -.8], [182, 1]]), eyeY: kf(f, [[130, .7], [146, .5], [176, .3], [182, -.4]]),
      mouth: lip('leonard1', f), smile: kf(f, [[180, 0], [186, .45]]), brow: .25 },
    armL: { sh: 10 + 62 * g, el: -20 + 4 * g, hand: 'open' },
  });
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, leonard: leo, sheldon: sheldonStand(f, { face: { turn: -.5, eyeX: -1 } }) }} />
      <Caption x={140} y={96} name="Leonard" until={SHOTS.explanation[1]} phrases={[
        { at: CUES.iNeeded, tokens: [{ t: 'I needed' }] }, { at: CUES.spaceFood, tokens: [{ t: 'space for the' }, { t: 'food.', c: C.gold }] }]} />
    </>
  );
};
