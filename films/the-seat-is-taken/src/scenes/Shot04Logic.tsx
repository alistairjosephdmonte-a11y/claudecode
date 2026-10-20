// SHOT 04 · THE LOGIC — medium on Sheldon, a close-up of the raised finger, back to his face. Diagram line-draws beside him.
import React from 'react';
import { World } from '../components/World';
import { Caption } from '../components/Type';
import { CouchDiagram } from '../components/Diagram';
import { kf, leonard, lip, sheldonStand, held } from './common';
import { PaperBag } from '../components/Set';
import { C, CUES, SHOTS } from '../config';

export const Shot04Logic: React.FC<{ f: number }> = ({ f }) => {
  const handCU = f >= 222 && f < 244;
  const cam = handCU ? { cx: 1585, cy: 395, z: kf(f, [[222, 3.3], [244, 3.5]]) } : { cx: kf(f, [[190, 1550], [272, 1565]]), cy: 420, z: kf(f, [[190, 2.2], [272, 2.32]]) };
  const raise = kf(f, [[192, 0], [200, 1]]);
  const g = Math.sin(Math.max(0, f - 200) * .28) * (f > 200 && f < 262 ? 1 : 0);        // three small precise gestures
  const sh = sheldonStand(f, {
    lean: kf(f, [[190, 0], [200, -5]]),
    face: { turn: -.15, eyeX: kf(f, [[190, -.3], [230, .2], [250, -.2]]), brow: .35, mouth: lip('sheldon2', f), lids: 0 },
    armR: { sh: -6 - 34 * raise + 5 * g, el: 4 - 144 * raise - 6 * g, hand: raise > .5 ? 'point' : 'hold' },
    armL: { sh: 5, el: -3, hand: 'hold' },
  });
  sh.holdL = held(sh.armL!, <PaperBag x={0} y={88} s={.75} />, 0);
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, sheldon: sh, leonard: leonard(f, { eat: true }) }} />
      <CouchDiagram x={1110} y={80} at={196} until={SHOTS.logic[1]} />
      <Caption x={1110} y={590} name="Sheldon" until={SHOTS.logic[1]} size={54} maxW={720} phrases={[
        { at: CUES.seating, tokens: [{ t: 'The seating arrangement' }] }, { at: CUES.follows, tokens: [{ t: 'follows a' }] },
        { at: CUES.geometry, tokens: [{ t: 'specific geometry.', c: C.gold }] }]} />
    </>
  );
};
