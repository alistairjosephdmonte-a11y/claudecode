// SHOT 07 · THE PUNCHLINE — Sheldon, completely serious; then Leonard's resigned reaction in the silence.
import React from 'react';
import { World } from '../components/World';
import { Caption } from '../components/Type';
import { kf, leonard, lip, sheldonStand, pennySeated, chew } from './common';
import { C, CUES, SHOTS } from '../config';

export const Shot07Punchline: React.FC<{ f: number }> = ({ f }) => {
  const reaction = f >= 410;
  const cam = reaction ? { cx: 964, cy: 445, z: kf(f, [[410, 2.35], [420, 2.45]]) } : { cx: 1390, cy: 380, z: kf(f, [[344, 2.55], [410, 2.8]]) };
  const sh = sheldonStand(f, {
    face: { turn: kf(f, [[344, -.55], [360, -.55], [366, -.1]]), eyeX: kf(f, [[344, -1], [360, -1], [366, 0]]), eyeY: kf(f, [[344, .55], [352, .55], [354, .2], [360, .2], [366, 0]]),
      brow: .15, frown: .35, mouth: lip('sheldon3', f), lids: 0 },
  });
  const leo = leonard(f, { bob: reaction ? -6 : 0, face: reaction ? { lids: kf(f, [[410, .1], [416, .5]]), sad: .7, eyeX: 0, eyeY: .5, mouth: 0, turn: 0 } : { eyeX: 1 } });
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, squash: [0, 0, .6], sheldon: sh, leonard: leo, penny: pennySeated(f, { face: { mouth: chew(f, true) } }) }} />
      <Caption x={140} y={110} name="Sheldon" until={SHOTS.punchline[1]} size={66} maxW={760} phrases={[
        { at: CUES.thisIs, tokens: [{ t: 'This is' }] }, { at: CUES.precisely, tokens: [{ t: 'precisely' }] },
        { at: CUES.whyWe, tokens: [{ t: 'why we need' }] }, { at: CUES.rules, tokens: [{ t: 'rules.', c: C.red, scale: 1.35 }] }]} />
    </>
  );
};
