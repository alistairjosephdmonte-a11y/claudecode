import React from 'react';
import { C, STAGE } from '../config';

// The couch. cx = centre; w = width; compress = 0..1 (seat squash); cushionDx = striped cushion offset.
export function Couch({ cx = STAGE.couchX, w = STAGE.couchW, compress = 0, cushionDx = 0, cushion = true, seats = 3 }) {
  const top = STAGE.seatY - 210, seat = STAGE.seatY, base = STAGE.floor - 40;
  const x0 = cx - w / 2, x1 = cx + w / 2, sq = compress * 10;
  const cw = (w - 220) / seats;
  return (
    <g>
      <rect x={x0 + 40} y={top} width={w - 80} height={230} rx={40} fill={C.couchDark} />
      {Array.from({ length: seats }).map((_, i) => (
        <rect key={i} x={x0 + 112 + i * cw} y={top + 24} width={cw - 12} height={180} rx={28} fill={C.couch} />
      ))}
      {Array.from({ length: seats }).map((_, i) => (
        <rect key={'s' + i} x={x0 + 108 + i * cw} y={seat - 18 + sq} width={cw - 4} height={74 - sq} rx={22} fill={C.couchLight} />
      ))}
      <rect x={x0 + 70} y={seat + 50} width={w - 140} height={base - seat - 50} rx={18} fill={C.couch} />
      {[x0, x1 - 120].map((ax, i) => <rect key={i} x={ax} y={seat - 110} width={120} height={base - seat + 110} rx={40} fill={C.couchDark} />)}
      {[x0 + 60, x1 - 90].map((lx, i) => <rect key={'l' + i} x={lx} y={base} width={30} height={STAGE.floor - base} rx={6} fill="#4A2616" />)}
      {cushion && <StripedCushion x={x0 + 140 + cushionDx} y={top + 70} />}
    </g>
  );
}

const STRIPES = ['#168D70', '#D62D2D', '#F7F5EF', '#0879D9', '#FFB33F', '#7A3E8E', '#F7F5EF', '#D62D2D'];
export function StripedCushion({ x, y, w = 190, h = 128, rot = -6 }) {
  return (
    <g transform={`translate(${x},${y}) rotate(${rot},${w / 2},${h / 2})`}>
      <clipPath id={`cc${Math.round(x)}`}><rect width={w} height={h} rx={26} /></clipPath>
      <g clipPath={`url(#cc${Math.round(x)})`}>
        {STRIPES.map((c, i) => <rect key={i} x={0} y={(i * h) / STRIPES.length} width={w} height={h / STRIPES.length + 1} fill={c} />)}
      </g>
      <rect width={w} height={h} rx={26} fill="none" stroke={C.charcoal} strokeWidth="4" opacity="0.35" />
    </g>
  );
}

// Takeaway carton (generic white folded box, wire handle, simple red bands)
export function Carton({ x, y, s = 1, rot = 0, open = false }) {
  return (
    <g transform={`translate(${x},${y}) rotate(${rot}) scale(${s})`}>
      <path d="M-30,-70 Q0,-112 30,-70" fill="none" stroke="#9AA0A6" strokeWidth="4" />
      <path d="M-46,-70 L46,-70 L34,30 L-34,30 Z" fill={C.white} stroke={C.charcoal} strokeWidth="4" strokeLinejoin="round" />
      <path d="M-46,-70 L0,-50 L46,-70" fill="none" stroke={C.charcoal} strokeWidth="3" />
      <rect x="-40" y="-20" width="80" height="8" fill={C.red} /><rect x="-38" y="-6" width="76" height="4" fill={C.red} />
      {open && [-14, 0, 14].map((fx, i) => <rect key={i} x={fx - 4} y={-104 + i * 6} width="9" height="46" rx="3" fill={C.gold} transform={`rotate(${(i - 1) * 9},${fx},-80)`} />)}
    </g>
  );
}

export const Fry = ({ x, y, rot = 0 }) => <rect x={x - 5} y={y - 26} width="11" height="52" rx="4" fill={C.gold} stroke="#B97A00" strokeWidth="2" transform={`rotate(${rot},${x},${y})`} />;

// Doorway with a door panel that swings open (open: 0..1)
export function Door({ x, open = 0 }) {
  const top = 230, w = 300, h = STAGE.floor - top;
  return (
    <g>
      <rect x={x - 22} y={top - 22} width={w + 44} height={h + 22} fill="#5A3A26" />
      <rect x={x} y={top} width={w} height={h} fill="#2B1C12" />
      <g transform={`translate(${x},0) scale(${1 - open * 0.78},1)`}>
        <rect x={0} y={top} width={w} height={h} fill="#7B5236" />
        <rect x={26} y={top + 30} width={w - 52} height={h * 0.42} rx={6} fill="none" stroke="#5A3A26" strokeWidth="6" />
        <rect x={26} y={top + 60 + h * 0.42} width={w - 52} height={h * 0.42} rx={6} fill="none" stroke="#5A3A26" strokeWidth="6" />
        <circle cx={w - 36} cy={top + h * 0.52} r={11} fill={C.gold} />
      </g>
    </g>
  );
}

// Small outline couch icon used in the opening shot
export const CouchIcon = ({ x, y, s = 1, op = 1 }) => (
  <g transform={`translate(${x},${y}) scale(${s})`} opacity={op} fill="none" stroke={C.charcoal} strokeWidth="7" strokeLinejoin="round" strokeLinecap="round">
    <path d="M-80,0 L-80,-46 Q-80,-60 -66,-60 L66,-60 Q80,-60 80,-46 L80,0" />
    <path d="M-100,10 L-100,-24 Q-100,-34 -90,-34 Q-80,-34 -80,-24 L-80,0 L80,0 L80,-24 Q80,-34 90,-34 Q100,-34 100,-24 L100,10 Z" />
    <path d="M-88,10 L-88,26 M88,10 L88,26" />
  </g>
);

export function Arrow({ x1, y1, x2, y2, k = 1, color = C.red, w = 9 }) {
  const ex = x1 + (x2 - x1) * k, ey = y1 + (y2 - y1) * k, a = Math.atan2(y2 - y1, x2 - x1), hs = 26;
  return (
    <g stroke={color} strokeWidth={w} strokeLinecap="round" fill="none" opacity={k > 0 ? 1 : 0}>
      <line x1={x1} y1={y1} x2={ex} y2={ey} />
      {k > 0.6 && <path d={`M${ex - hs * Math.cos(a - 0.5)},${ey - hs * Math.sin(a - 0.5)} L${ex},${ey} L${ex - hs * Math.cos(a + 0.5)},${ey - hs * Math.sin(a + 0.5)}`} />}
    </g>
  );
}
