// SHOT 01 · THE ARRIVAL — lateral move, then a small push toward Sheldon as he notices the cushion.
import React from 'react';
import { World } from '../components/World';
import { LowerThird } from '../components/Type';
import { kf, leonard, sheldonStand, toScreen } from './common';
import { CUES, SHOTS } from '../config';

export const Shot01Arrival: React.FC<{ f: number }> = ({ f }) => {
  const cam = { cx: kf(f, [[0, 1040], [40, 985], [50, 985], [84, 1330]]), cy: kf(f, [[0, 540], [50, 540], [84, 470]]), z: kf(f, [[0, 1], [50, 1], [84, 1.18]]) };
  const walking = f < 40 || (f > 53 && f < 64);
  const x = kf(f, [[0, 1730], [40, 1505], [54, 1505], [64, 1460]]);
  const sh = sheldonStand(f, {
    x, walk: walking ? f * .48 : 0, bob: walking ? Math.abs(Math.sin(f * .48)) * 6 : 0,
    face: { turn: kf(f, [[60, 0], [76, -.75]]), eyeX: kf(f, [[60, 0], [72, -1]]), eyeY: kf(f, [[68, 0], [78, .6]]), brow: kf(f, [[74, 0], [80, .5]]), lids: 0 },
  });
  const [ax, ay] = toScreen(cam, x - 95, 150);
  return (
    <>
      <World cam={cam} s={{ frame: f, spotShift: 1, foodOnSpot: true, sheldon: sh, leonard: leonard(f, { eat: true }) }} />
      <LowerThird x={ax} y={ay - 40} small="Even a couch has" big="RULES" atSmall={CUES.narrA} atBig={CUES.narrB} until={SHOTS.arrival[1] + 2} align="right" />
    </>
  );
};
