// One shared world + a 2.5D camera. Background, couch layer and foreground move with different
// parallax so pushes and pans have depth. Each shot only changes camera and character state.
import React from 'react';
import { AbsoluteFill, interpolate, Easing } from 'remotion';
import { Background, Couch, CoffeeTable, TakeoutBox, COUCH } from './Set';
import { Character, Pose, SHELDON, LEONARD, PENNY } from './Characters';
import lips from '../generated/lipsync.json';
import { VOICE } from '../config';

export type Cam = { cx: number; cy: number; z: number };
export type WorldState = {
  frame: number; spotShift: number; foodOnSpot: boolean; foodOnTable?: boolean; squash?: number[];
  sheldon?: Pose | null; leonard?: Pose | null; penny?: Pose | null;
  sheldonFront?: boolean; // standing Sheldon drawn in front of the couch layer (default)
};

const E = Easing.bezier(.45, 0, .2, 1);
// keyframes: [[frame, value], ...] → value at f (eased, clamped)
export const kf = (f: number, keys: [number, number][], ease = E) => {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [a, va] = keys[i], [b, vb] = keys[i + 1];
    if (f <= b) return interpolate(f, [a, b], [va, vb], { easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  }
  return keys[keys.length - 1][1];
};
// mouth openness from the voice's envelope (0 when the line is not playing)
export const lip = (id: keyof typeof VOICE, f: number) => {
  const L = (lips as Record<string, number[]>)[id]; const i = f - VOICE[id];
  if (!L || i < 0 || i >= L.length) return 0;
  return Math.min(1, (L[i] * .7 + (L[i - 1] ?? 0) * .3) * 1.1);
};
export const chew = (f: number, on: boolean) => on ? Math.max(0, Math.sin(f * .55)) * .35 : 0;
export const blink = (f: number, seed: number) => { const p = (f + seed * 37) % 97; return p < 3 ? [1, .9, .4][p] : 0; };

const layer = (cam: Cam, p: number) => {
  const cx = 960 + (cam.cx - 960) * p, cy = 540 + (cam.cy - 540) * p;
  return `translate(960 540) scale(${cam.z}) translate(${-cx} ${-cy})`;
};

export const World: React.FC<{ cam: Cam; s: WorldState }> = ({ cam, s }) => (
  <AbsoluteFill>
    <svg viewBox="0 0 1920 1080" width={1920} height={1080} style={{ position: 'absolute' }}>
      <g transform={layer(cam, .86)}><Background frame={s.frame} /></g>
      <g transform={layer(cam, 1)}>
        <Couch spotShift={s.spotShift} squash={s.squash} />
        {s.foodOnSpot && <g transform={`translate(${-34 * s.spotShift} 0)`}><TakeoutBox x={COUCH.cushions[0] - 40} y={688} s={.9} open /><TakeoutBox x={COUCH.cushions[0] + 50} y={690} s={.85} /></g>}
        {s.leonard && <Character s={LEONARD} p={s.leonard} />}
        {s.penny && (s.penny.sit ?? 0) > .01 && <Character s={PENNY} p={s.penny} />}
        {s.sheldon && <Character s={SHELDON} p={s.sheldon} />}
        {s.penny && (s.penny.sit ?? 0) <= .01 && <Character s={PENNY} p={s.penny} />}
      </g>
      <g transform={layer(cam, 1.14)}><CoffeeTable foodOnTable={s.foodOnTable} /></g>
      {/* warm light falloff */}
      <defs><radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stopColor="#3a2414" stopOpacity="0" /><stop offset="1" stopColor="#3a2414" stopOpacity=".38" /></radialGradient></defs>
      <rect width={1920} height={1080} fill="url(#vig)" />
    </svg>
  </AbsoluteFill>
);

// common poses
export const LEO_SEAT = { x: COUCH.cushions[1], y: 842 };
export const PENNY_SEAT = { x: COUCH.cushions[2], y: 842 };
export const SPOT_SEAT = { x: COUCH.cushions[0], y: 842 };
export const SHELDON_STAND = { x: 1460, y: 905 };
