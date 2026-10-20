// SHOT 02 · THE VIOLATION — close-up on Sheldon (eyes: Leonard → cushion → Leonard, small point), then Leonard's reaction.
import React from 'react';
import { World } from '../components/World';
import { Caption } from '../components/Type';
import { kf, leonard, sheldonStand, lip } from './common';
import { C, CUES, SHOTS } from '../config';

export const Shot02Violation: React.FC<{ f: number }> = ({ f }) => {
  const reaction = f >= 116;
  const cam = reaction ? { cx: 964, cy: 440, z: kf(f, [[116, 2.3], [128, 2.4]]) } : { cx: 1360, cy: 405, z: kf(f, [[84, 2.45], [116, 2.6]]) };
  const eyeY = kf(f, [[90, .1], [94, .85], [100, .85], [104, .1]]);
  const point = kf(f, [[95, 0], [101, 1], [110, 1], [116, .4]]);
  const sh = sheldonStand(f, {
    face: { turn: -.55, eyeX: -1, eyeY, brow: kf(f, [[84, .4], [96, .7]]), frown: .2, mouth: lip('sheldon1', f) },
    armL: { sh: 5 + 70 * point, el: -3 + 8 * point, hand: point > .5 ? 'point' : 'open' },
  });
  const leo = leonard(f, { eat: !reaction, face: reaction ? { eyeX: 1, eyeY: -.7, brow: kf(f, [[116, 0], [121, .6]]), mouth: 0, turn: .25 } : {} });
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, sheldon: sh, leonard: leo }} />
      <Caption x={140} y={770} name="Sheldon" until={SHOTS.violation[1]} phrases={[
        { at: CUES.why, tokens: [{ t: 'Why' }] }, { at: CUES.haveYou, tokens: [{ t: 'have you' }] }, { at: CUES.movedIt, tokens: [{ t: 'moved', c: C.red }, { t: 'it?' }] }]} />
    </>
  );
};
