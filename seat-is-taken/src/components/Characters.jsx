// Headless flat-vector outfit silhouettes. Origin is the hip centre; y grows downward.
// pose: 'stand' (feet 300 below hip) or 'sit' (lap at hip, shins to the floor).
import React from 'react';
import { C, STAGE } from '../config';

const OUTFITS = {
  sheldon: { top: '#1F5FB8', sleeve: '#C9B79C', short: true, under: '#C9B79C', pants: '#7A5A3A', shoe: '#F1F1F1', logo: 'atom' },
  leonard: { top: 'plaid', sleeve: 'plaid', short: false, under: '#333333', pants: '#3E5276', shoe: '#E8E8E8', open: true, glasses: true },
  penny: { top: '#7EC8E3', sleeve: '#7EC8E3', short: false, under: '#F4A6B8', skirt: '#E8668C', shoe: '#C94F72', open: true, legs: C.skin },
  extraA: { top: '#6B3FA0', sleeve: '#6B3FA0', short: false, under: '#F08A24', pants: '#55663A', shoe: '#E8E8E8', open: true },
  extraB: { top: '#2E9E4A', sleeve: '#D8D2C2', short: true, under: '#D8D2C2', pants: '#B49A6B', shoe: '#EDEDED', logo: 'ring', strap: true },
};

const Plaid = () => (
  <pattern id="plaid" width="44" height="44" patternUnits="userSpaceOnUse">
    <rect width="44" height="44" fill="#D63A2F" />
    <rect x="0" y="14" width="44" height="9" fill="#B02A22" opacity="0.8" />
    <rect x="16" y="0" width="9" height="44" fill="#B02A22" opacity="0.8" />
    <rect x="0" y="34" width="44" height="3" fill="#F2B04A" opacity="0.7" />
    <rect x="35" y="0" width="3" height="44" fill="#F2B04A" opacity="0.7" />
  </pattern>
);
export const Defs = () => <defs><Plaid /></defs>;

const fill = (v) => (v === 'plaid' ? 'url(#plaid)' : v);

function Arm({ side, angle, o, len = 236 }) {
  // side: -1 left, +1 right (viewer's). angle in degrees: 0 hangs down, positive swings outward.
  const sx = side * 122, sy = -252;
  return (
    <g transform={`translate(${sx},${sy}) rotate(${-side * angle})`}>
      <rect x={-23} y={-6} width={46} height={len} rx={22} fill={fill(o.sleeve)} />
      {o.short && <path d={`M-30,-12 L30,-12 L27,78 L-27,78 Z`} fill={fill(o.top)} />}
      <circle cx={0} cy={len + 4} r={21} fill={C.skin} />
    </g>
  );
}

function Logo({ o }) {
  if (o.logo === 'atom')
    return (
      <g transform="translate(0,-170)" stroke="#BFE2FF" strokeWidth="5" fill="none">
        {[0, 60, -60].map((r) => <ellipse key={r} rx="46" ry="16" transform={`rotate(${r})`} />)}
        <circle r="7" fill="#BFE2FF" stroke="none" />
      </g>
    );
  if (o.logo === 'ring')
    return <g transform="translate(0,-170)"><circle r="30" fill="#F7F5EF" /><circle r="17" fill="#2E9E4A" /><rect x="-20" y="-5" width="40" height="10" fill="#F7F5EF" /></g>;
  return null;
}

export function Person({ who, x, y, pose = 'stand', armL = 4, armR = 4, tilt = 0, scale = 1, breathe = 0, footTap = 0 }) {
  const o = OUTFITS[who];
  const sit = pose === 'sit';
  const shinLen = STAGE.floor - STAGE.seatY - 34; // sitting shins reach the shared floor line
  const legs = sit ? (
    <g>
      <rect x={-92} y={-18} width={184} height={70} rx={26} fill={o.skirt || o.pants} />
      {[-1, 1].map((s) => (
        <g key={s} transform={s === 1 && footTap ? `rotate(${-footTap},${s * 50},40)` : undefined}>
          <rect x={s * 50 - 27} y={40} width={54} height={shinLen} rx={18} fill={o.legs || o.pants} />
          <ellipse cx={s * 50 + s * 6} cy={40 + shinLen + 6} rx={38} ry={16} fill={o.shoe} stroke={C.charcoal} strokeWidth="3" />
        </g>
      ))}
      {o.skirt && <path d="M-100,-20 L100,-20 L118,70 L-118,70 Z" fill={o.skirt} />}
    </g>
  ) : (
    <g>
      {o.skirt ? (
        <>
          {[-1, 1].map((s) => <rect key={s} x={s * 42 - 22} y={40} width={44} height={262} rx={16} fill={o.legs} />)}
          <path d="M-96,-22 L96,-22 L128,150 L-128,150 Z" fill={o.skirt} />
        </>
      ) : (
        [-1, 1].map((s) => <rect key={s} x={s * 45 - 40} y={-14} width={80} height={312} rx={22} fill={o.pants} />)
      )}
      {[-1, 1].map((s) => <ellipse key={s} cx={s * 50 + s * 8} cy={304} rx={44} ry={17} fill={o.shoe} stroke={C.charcoal} strokeWidth="3" />)}
    </g>
  );
  const torsoH = sit ? 262 : 272;
  return (
    <g transform={`translate(${x},${y}) scale(${scale}) rotate(${tilt},0,0)`}>
      {legs}
      <g transform={`translate(0,0) scale(1,${1 + breathe})`}>
        <Arm side={-1} angle={armL} o={o} />
        <Arm side={1} angle={armR} o={o} />
        {/* torso */}
        <path d={`M-104,-${torsoH} Q-112,-${torsoH - 10} -108,-${torsoH - 40} L-92,6 L92,6 L108,-${torsoH - 40} Q112,-${torsoH - 10} 104,-${torsoH} Z`} fill={o.open ? o.under : fill(o.top)} />
        {o.open && (
          <>
            <path d={`M-104,-${torsoH} L-30,-${torsoH} L-22,6 L-92,6 L-108,-${torsoH - 40} Z`} fill={fill(o.top)} />
            <path d={`M104,-${torsoH} L30,-${torsoH} L22,6 L92,6 L108,-${torsoH - 40} Z`} fill={fill(o.top)} />
          </>
        )}
        <Logo o={o} />
        {o.strap && <path d={`M-96,-${torsoH - 6} L80,-10`} stroke="#5B4632" strokeWidth="16" strokeLinecap="round" />}
        {/* collar / neck stub (headless by design) */}
        <path d={`M-34,-${torsoH + 2} Q0,-${torsoH - 34} 34,-${torsoH + 2}`} fill="none" stroke={C.charcoal} strokeWidth="6" strokeLinecap="round" />
        <rect x={-22} y={-torsoH - 24} width={44} height={24} rx={8} fill={C.skin} />
        {o.glasses && (
          <g transform={`translate(0,-${torsoH + 70})`} stroke={C.charcoal} strokeWidth="6" fill="none">
            <rect x={-56} y={-16} width={46} height={32} rx={10} /><rect x={10} y={-16} width={46} height={32} rx={10} /><path d="M-10,-4 L10,-4" />
          </g>
        )}
      </g>
    </g>
  );
}
