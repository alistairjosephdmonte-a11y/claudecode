// Explanatory couch diagram: thin blue line-draw, one gold marker for Sheldon's spot,
// two measurement labels and a small arrow. A graphic panel, not an object in the room.
import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';
import { C, FONT } from '../config';
import { inOut } from './Type';

const draw = (f: number, a: number, b: number) => interpolate(f, [a, b], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(.4, 0, .2, 1) });

export const CouchDiagram: React.FC<{ x: number; y: number; at: number; until: number }> = ({ x, y, at, until }) => {
  const f = useCurrentFrame();
  const a = inOut(f, at - 4, until, 5, 6);
  if (a <= 0) return null;
  const L = (d: string, t0: number, t1: number, w = 3, col = C.blue) =>
    <path d={d} pathLength={1} fill="none" stroke={col} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1" strokeDashoffset={draw(f, t0, t1)} />;
  const lab = (t: number) => interpolate(f, [t, t + 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const mk = interpolate(f, [at + 20, at + 26, at + 30], [0, 1.25, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const txt = { fontFamily: FONT, fontWeight: 700, letterSpacing: '0.08em' } as const;
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: 720, height: 470, opacity: a }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(16,29,53,.88)', borderRadius: 14 }} />
      <div style={{ position: 'absolute', left: 30, top: 22, ...txt, fontSize: 20, color: C.blue }}>FIG. 1 — SEATING ARRANGEMENT</div>
      <svg width={720} height={470} style={{ position: 'absolute', inset: 0 }}>
        {/* couch outline, top-down */}
        {L('M80 140 L640 140 L640 330 L80 330 Z', at, at + 14, 3)}
        {L('M80 140 L80 330 M120 175 L600 175', at + 4, at + 16, 2)}
        {[0, 1, 2].map(i => L(`M${120 + i * 160} 185 L${270 + i * 160} 185 L${270 + i * 160} 315 L${120 + i * 160} 315 Z`, at + 8 + i * 3, at + 20 + i * 3, 2.5))}
        {/* measurement: cushion width */}
        <g opacity={lab(at + 28)}>
          {L('M120 360 L270 360 M120 350 L120 370 M270 350 L270 370', at + 28, at + 34, 2)}
          <text x={195} y={398} textAnchor="middle" fill={C.white} style={{ ...txt, fontSize: 22 }}>0.58 M</text>
        </g>
        {/* measurement: viewing angle */}
        <g opacity={lab(at + 36)}>
          {L('M195 250 L195 80 M195 250 L330 92', at + 36, at + 44, 2)}
          <path d="M195 190 A60 60 0 0 1 238 207" fill="none" stroke={C.blue} strokeWidth={2} />
          <text x={262} y={74} fill={C.white} style={{ ...txt, fontSize: 22 }}>22.5° TO TV</text>
        </g>
        {/* Sheldon's spot */}
        <circle cx={195} cy={250} r={22 * mk} fill={C.gold} />
        <circle cx={195} cy={250} r={34 * mk} fill="none" stroke={C.gold} strokeWidth={2} opacity={.6} />
        {/* arrow + label */}
        <g opacity={lab(at + 44)}>
          {L('M520 420 Q380 420 228 268', at + 44, at + 52, 2.5, C.gold)}
          <path d="M228 268 l4 18 M228 268 l18 4" stroke={C.gold} strokeWidth={2.5} strokeLinecap="round" opacity={lab(at + 50)} />
          <text x={530} y={428} fill={C.gold} style={{ ...txt, fontSize: 22 }}>HIS SPOT</text>
        </g>
      </svg>
    </div>
  );
};
