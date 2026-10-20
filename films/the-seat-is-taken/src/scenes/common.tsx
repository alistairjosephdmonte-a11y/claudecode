import React from 'react';
import { Fries, Fry, PaperBag } from '../components/Set';
import { Pose, Arm } from '../components/Characters';
import { kf, chew, blink, lip, LEO_SEAT, PENNY_SEAT, SHELDON_STAND, Cam } from '../components/World';

// world → screen (camera layer factor 1)
export const toScreen = (cam: Cam, x: number, y: number) => [960 + (x - cam.cx) * cam.z, 540 + (y - cam.cy) * cam.z];

// held props are counter-rotated so they stay upright in the hand
export const held = (a: Arm, node: React.ReactNode, dy = 14) => <g transform={`rotate(${-(a.sh + a.el)}) translate(0 ${dy})`}>{node}</g>;

// Leonard on the middle cushion with his fries; eats on a loop unless told otherwise
export const leonard = (f: number, o: { eat?: boolean; face?: any; armL?: Arm; fries?: number; bob?: number; lean?: number } = {}): Pose => {
  const eatCycle = (f % 46) / 46;
  const toMouth = o.eat ? Math.max(0, Math.sin(eatCycle * Math.PI * 2)) : 0;
  const armL: Arm = o.armL ?? { sh: 10 - 40 * toMouth, el: -20 - 120 * toMouth, hand: 'fist' };
  const armR: Arm = { sh: -10, el: 60, hand: 'hold' };
  return {
    ...LEO_SEAT, sit: 1, bob: o.bob ?? 0, lean: o.lean ?? 0,
    face: { eyeX: .6, eyeY: .2, mouth: chew(f, !!o.eat && toMouth < .2), lids: blink(f, 2), ...o.face },
    armL, armR, holdR: held(armR, <Fries x={0} y={22} s={.8} count={o.fries ?? 7} />),
  };
};

export const sheldonStand = (f: number, o: Partial<Pose> & { face?: any } = {}): Pose => {
  const armR: Arm = o.armR ?? { sh: -6, el: 4, hand: 'hold' };
  return {
    ...SHELDON_STAND, face: { lids: blink(f, 5), ...o.face },
    armL: { sh: 5, el: -3, hand: 'open' }, armR, holdR: armR.hand === 'hold' ? held(armR, <PaperBag x={0} y={88} s={.75} />, 0) : undefined,
    ...o,
  };
};

export const pennySeated = (f: number, o: { face?: any; armL?: Arm; armR?: Arm; holdL?: React.ReactNode; holdR?: React.ReactNode; lean?: number } = {}): Pose => ({
  ...PENNY_SEAT, sit: 1, lean: o.lean ?? 0,
  face: { smile: .5, lids: blink(f, 9), turn: -.2, eyeX: -.4, ...o.face },
  armL: o.armL ?? { sh: 14, el: -40, hand: 'open' }, armR: o.armR ?? { sh: -14, el: 40, hand: 'open' },
  holdL: o.holdL, holdR: o.holdR,
});

export { kf, chew, blink, lip, Fry };
