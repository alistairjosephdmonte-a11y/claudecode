// Original illustrated characters built as restrained 2.5D puppets: head turn, eyes, brows, mouth
// (lip-synced from the voice files), two-segment arms, stand / walk / sit. Designs stay fixed in every shot.
import React from 'react';
import { C } from '../config';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const O = { stroke: C.ink, strokeWidth: 3, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const };

export type Arm = { sh: number; el: number; hand?: 'open' | 'point' | 'fist' | 'up' | 'hold' };
export type Face = { turn?: number; tilt?: number; eyeX?: number; eyeY?: number; brow?: number; frown?: number; mouth?: number; smile?: number; lids?: number; sad?: number };
export type Pose = {
  x: number; y: number; scale?: number;
  sit?: number; walk?: number; lean?: number; bob?: number;
  face?: Face; armL?: Arm; armR?: Arm; holdL?: React.ReactNode; holdR?: React.ReactNode;
};

type Spec = {
  legLen: number; torso: number; neck: number; hr: number; hry: number; shoulderW: number; hipW: number; armU: number; armF: number;
  skin: string; skinSh: string; shirt: string; shirtSh: string; sleeve: string; pants: string; pantsSh: string; shoes: string;
  hairBack?: (hr: number, hry: number) => React.ReactNode; hairFront: (hr: number, hry: number, turn: number) => React.ReactNode;
  glasses?: boolean; chest?: (w: number, h: number) => React.ReactNode; jacket?: string; lips?: string;
};

const SEAT_H = 150;

const Hand: React.FC<{ kind: Arm['hand']; skin: string }> = ({ kind = 'open', skin }) => {
  const r = 17;
  return (
    <g>
      {kind === 'point' && <rect x={-5} y={8} width={10} height={34} rx={5} fill={skin} {...O} strokeWidth={2.5} />}
      {kind === 'up' && <rect x={-5} y={-34} width={10} height={32} rx={5} fill={skin} {...O} strokeWidth={2.5} />}
      <ellipse cx={0} cy={6} rx={r} ry={kind === 'fist' ? 15 : 19} fill={skin} {...O} strokeWidth={2.5} />
      {kind === 'open' && [-9, -3, 3, 9].map(x => <line key={x} x1={x} y1={14} x2={x * 1.1} y2={24} stroke={C.ink} strokeWidth={2} />)}
      <ellipse cx={-14} cy={0} rx={6} ry={10} fill={skin} {...O} strokeWidth={2.5} transform="rotate(25 -14 0)" />
    </g>
  );
};

const ArmG: React.FC<{ a: Arm; side: -1 | 1; s: Spec; hold?: React.ReactNode }> = ({ a, side, s, hold }) => {
  const w = 30;
  return (
    <g transform={`rotate(${a.sh})`}>
      <rect x={-w / 2} y={-8} width={w} height={s.armU + 12} rx={w / 2} fill={s.sleeve} {...O} />
      <g transform={`translate(0 ${s.armU}) rotate(${a.el})`}>
        <rect x={-w / 2 + 2} y={-8} width={w - 4} height={s.armF + 6} rx={(w - 4) / 2} fill={s.jacket && side ? s.sleeve : s.sleeve} {...O} />
        <rect x={-w / 2 + 3} y={s.armF - 22} width={w - 6} height={14} rx={5} fill={s.sleeve} stroke="none" />
        <g transform={`translate(0 ${s.armF + 6})`}>
          {hold}
          <Hand kind={a.hand} skin={s.skin} />
        </g>
      </g>
    </g>
  );
};

const Head: React.FC<{ s: Spec; f: Face }> = ({ s, f }) => {
  const turn = f.turn ?? 0, hr = s.hr, hry = s.hry;
  const fx = turn * hr * .32;
  const sp = hr * .36 * (1 - .22 * Math.abs(turn));
  const lids = Math.min(1, f.lids ?? 0);
  const ey = -hry * .04;
  const ex = (f.eyeX ?? 0) * 5.5, eyy = (f.eyeY ?? 0) * 5;
  const brow = f.brow ?? 0, frown = f.frown ?? 0, sad = f.sad ?? 0;
  const mouth = f.mouth ?? 0, smile = f.smile ?? 0;
  const my = hry * .5;
  return (
    <g transform={`rotate(${f.tilt ?? 0})`}>
      {s.hairBack?.(hr, hry)}
      {/* ears */}
      <ellipse cx={-hr + 2 + Math.max(0, turn) * 6} cy={4} rx={10} ry={16} fill={s.skin} {...O} opacity={turn > .6 ? 0 : 1} />
      <ellipse cx={hr - 2 + Math.min(0, turn) * 6} cy={4} rx={10} ry={16} fill={s.skin} {...O} opacity={turn < -.6 ? 0 : 1} />
      <ellipse cx={0} cy={0} rx={hr} ry={hry} fill={s.skin} {...O} />
      <path d={`M${-hr * .7} ${hry * .55} Q0 ${hry * 1.08} ${hr * .7} ${hry * .55}`} fill="none" stroke={s.skinSh} strokeWidth={6} opacity={.5} />
      {[-1, 1].map(k => {
        const x = fx + k * sp;
        return (
          <g key={k}>
            <ellipse cx={x} cy={ey} rx={11} ry={13 * (1 - lids * .85)} fill="#fff" {...O} strokeWidth={2.5} />
            {lids < .8 && <circle cx={x + ex} cy={ey + eyy * (1 - lids)} r={6} fill="#2a2420" />}
            {lids > .05 && <path d={`M${x - 12} ${ey - 13 + 26 * lids * .45} L${x + 12} ${ey - 13 + 26 * lids * .45}`} stroke={C.ink} strokeWidth={2.5} />}
            {/* brow: raise, frown (inner end down), sad (inner end up) */}
            <line x1={x - 13} y1={ey - 25 - brow * 9 + (k === 1 ? frown * 7 - sad * 6 : -frown * 2 + sad * 2)}
              x2={x + 13} y2={ey - 25 - brow * 9 + (k === -1 ? frown * 7 - sad * 6 : -frown * 2 + sad * 2)} stroke="#3a2a20" strokeWidth={5} strokeLinecap="round" />
          </g>
        );
      })}
      {s.glasses && (
        <g fill="none" stroke="#1d1a18" strokeWidth={5}>
          <rect x={fx - sp - 21} y={ey - 17} width={42} height={33} rx={7} />
          <rect x={fx + sp - 21} y={ey - 17} width={42} height={33} rx={7} />
          <line x1={fx - sp + 21} y1={ey - 4} x2={fx + sp - 21} y2={ey - 4} />
        </g>
      )}
      <path d={`M${fx + turn * 8} ${hry * .1} q${-6 + turn * 4} 14 ${2 + turn * 6} 20`} fill="none" stroke={s.skinSh} strokeWidth={3.5} />
      {mouth > .08
        ? <g><ellipse cx={fx + turn * 4} cy={my} rx={14 + mouth * 4} ry={3 + mouth * 12} fill="#5a2420" {...O} strokeWidth={2.5} /><ellipse cx={fx + turn * 4} cy={my + mouth * 7} rx={8} ry={3 * mouth} fill="#c8545a" /></g>
        : <path d={`M${fx - 16 + turn * 4} ${my} Q${fx + turn * 4} ${my + smile * 12} ${fx + 16 + turn * 4} ${my - (smile < 0 ? 0 : 0)}`} fill="none" stroke="#5a2420" strokeWidth={3.5} />}
      {s.hairFront(hr, hry, turn)}
    </g>
  );
};

export const Character: React.FC<{ s: Spec; p: Pose }> = ({ s, p }) => {
  const sit = p.sit ?? 0, walk = p.walk ?? 0, lean = p.lean ?? 0;
  const hipH = lerp(s.legLen, SEAT_H, sit) + (p.bob ?? 0);
  const kneeH = lerp(s.legLen * .5, SEAT_H - 18, sit);
  const hipY = -hipH, shY = hipY - s.torso, headY = shY - s.neck - s.hry * .85;
  const lw = s.hipW * .42;
  const legs = [-1, 1].map(k => {
    const spread = lerp(s.hipW * .26, s.hipW * .34, sit);
    const swing = walk ? Math.sin(walk) * 16 * k : 0;
    if (sit > .5) {
      return (
        <g key={k}>
          <rect x={k * spread - lw * .55} y={hipY - 6} width={lw * 1.1} height={hipH - kneeH + 34} rx={lw * .5} fill={s.pants} {...O} />
          <rect x={k * spread - lw * .45} y={-kneeH} width={lw * .9} height={kneeH - 4} rx={lw * .4} fill={s.pantsSh} {...O} />
          <ellipse cx={k * spread} cy={-6} rx={lw * .75} ry={13} fill={s.shoes} {...O} />
        </g>
      );
    }
    return (
      <g key={k} transform={`rotate(${swing} ${k * spread} ${hipY})`}>
        <rect x={k * spread - lw / 2} y={hipY - 6} width={lw} height={hipH} rx={lw * .45} fill={k === 1 ? s.pantsSh : s.pants} {...O} />
        <ellipse cx={k * spread + k * 6} cy={-8} rx={lw * .72} ry={13} fill={s.shoes} {...O} />
      </g>
    );
  });
  const torsoPath = `M${-s.shoulderW / 2} ${shY + 18} Q${-s.shoulderW / 2} ${shY} ${-s.shoulderW / 2 + 22} ${shY} L${s.shoulderW / 2 - 22} ${shY} Q${s.shoulderW / 2} ${shY} ${s.shoulderW / 2} ${shY + 18} L${s.hipW / 2} ${hipY + 4} L${-s.hipW / 2} ${hipY + 4} Z`;
  const armL: Arm = p.armL ?? { sh: 8, el: -6, hand: 'open' }, armR: Arm = p.armR ?? { sh: -8, el: 6, hand: 'open' };
  return (
    <g transform={`translate(${p.x} ${p.y}) scale(${p.scale ?? 1})`}>
      <ellipse cx={0} cy={2} rx={s.hipW * .9} ry={12} fill="#000" opacity={.18} />
      {legs}
      <g transform={`rotate(${lean} 0 ${hipY})`}>
        <path d={torsoPath} fill={s.shirt} {...O} />
        {s.jacket && <><path d={`M${-s.shoulderW / 2} ${shY + 18} Q${-s.shoulderW / 2} ${shY} ${-s.shoulderW / 2 + 22} ${shY} L${-14} ${shY} L${-20} ${hipY + 4} L${-s.hipW / 2} ${hipY + 4} Z`} fill={s.jacket} {...O} />
          <path d={`M${s.shoulderW / 2} ${shY + 18} Q${s.shoulderW / 2} ${shY} ${s.shoulderW / 2 - 22} ${shY} L${14} ${shY} L${20} ${hipY + 4} L${s.hipW / 2} ${hipY + 4} Z`} fill={s.jacket} {...O} /></>}
        {s.chest?.(s.shoulderW, s.torso) && <g transform={`translate(0 ${shY + s.torso * .38})`}>{s.chest(s.shoulderW, s.torso)}</g>}
        <rect x={-14} y={shY - s.neck - 4} width={28} height={s.neck + 12} fill={s.skin} {...O} />
        <path d={`M-22 ${shY} Q0 ${shY + 16} 22 ${shY}`} fill={s.skin} {...O} strokeWidth={2.5} />
        <g transform={`translate(0 ${headY})`}><Head s={s} f={p.face ?? {}} /></g>
        <g transform={`translate(${-s.shoulderW / 2 + 10} ${shY + 14})`}><ArmG a={armL} side={-1} s={s} hold={p.holdL} /></g>
        <g transform={`translate(${s.shoulderW / 2 - 10} ${shY + 14})`}><ArmG a={armR} side={1} s={s} hold={p.holdR} /></g>
      </g>
    </g>
  );
};

// ---------- the three designs (original; not likenesses of any actor) ----------
export const SHELDON: Spec = {
  legLen: 300, torso: 205, neck: 18, hr: 50, hry: 62, shoulderW: 128, hipW: 104, armU: 112, armF: 104,
  skin: '#f1c9a5', skinSh: '#d9a77f', shirt: '#c8463c', shirtSh: '#a8352d', sleeve: '#8d939c', pants: '#b59a6e', pantsSh: '#a1865b', shoes: '#5a4434',
  hairFront: (hr, hry, turn) => <path d={`M${-hr - 2} ${-hry * .2} Q${-hr} ${-hry - 14} ${-6 + turn * 6} ${-hry - 10} Q${hr + 4} ${-hry - 8} ${hr + 2} ${-hry * .25} Q${hr * .4} ${-hry * .62} ${-hr * .2 + turn * 5} ${-hry * .7} Q${-hr * .6} ${-hry * .62} ${-hr - 2} ${-hry * .2} Z`} fill="#4a3022" {...O} />,
  chest: () => (
    <g>
      <circle r={30} fill="#f5bc35" stroke={C.ink} strokeWidth={2.5} />
      {[0, 60, 120].map(a => <ellipse key={a} rx={22} ry={8} fill="none" stroke="#a8352d" strokeWidth={3} transform={`rotate(${a})`} />)}
      <circle r={4} fill="#a8352d" />
    </g>
  ),
};
export const LEONARD: Spec = {
  legLen: 240, torso: 188, neck: 14, hr: 50, hry: 59, shoulderW: 124, hipW: 104, armU: 98, armF: 92,
  skin: '#efc29c', skinSh: '#d69f77', shirt: '#3f6fa8', shirtSh: '#335c8c', sleeve: '#6f7a4a', pants: '#3d5576', pantsSh: '#34496a', shoes: '#d8d2c6',
  jacket: '#6f7a4a', glasses: true,
  hairFront: (hr, hry) => (
    <g fill="#3a2a20" {...O} strokeWidth={2.5}>
      {[[-hr * .85, -hry * .55, 20], [-hr * .5, -hry * .85, 22], [-hr * .05, -hry * .98, 23], [hr * .42, -hry * .88, 22], [hr * .82, -hry * .58, 19], [-hr * .95, -hry * .15, 15], [hr * .96, -hry * .2, 14], [-hr * .25, -hry * .72, 18], [hr * .2, -hry * .72, 18]]
        .map(([x, y, r], i) => <circle key={i} cx={x} cy={y} r={r} />)}
    </g>
  ),
};
export const PENNY: Spec = {
  legLen: 258, torso: 188, neck: 16, hr: 47, hry: 57, shoulderW: 112, hipW: 100, armU: 100, armF: 94,
  skin: '#f3cba8', skinSh: '#dda882', shirt: '#d9667c', shirtSh: '#c0546a', sleeve: '#d9667c', pants: '#2f3f5c', pantsSh: '#283651', shoes: '#8a5a3a',
  hairBack: (hr, hry) => <path d={`M${-hr - 10} ${-hry * .3} Q${-hr - 26} ${hry * 1.2} ${-hr - 8} ${hry * 1.9} L${hr + 8} ${hry * 1.9} Q${hr + 26} ${hry * 1.2} ${hr + 10} ${-hry * .3} Z`} fill="#e3b85c" {...O} />,
  hairFront: (hr, hry, turn) => <path d={`M${-hr - 6} ${hry * .1} Q${-hr - 6} ${-hry - 16} ${turn * 8} ${-hry - 12} Q${hr + 8} ${-hry - 10} ${hr + 6} ${hry * .05} Q${hr * .6} ${-hry * .5} ${hr * .1 + turn * 6} ${-hry * .58} Q${-hr * .5} ${-hry * .35} ${-hr * .7} ${hry * .02} Q${-hr * .85} ${-hry * .25} ${-hr - 6} ${hry * .1} Z`} fill="#e8c06a" {...O} />,
};
