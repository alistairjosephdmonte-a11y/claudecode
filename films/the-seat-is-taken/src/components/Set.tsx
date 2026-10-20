// The apartment: one fixed world (1920×1080 units) so the couch, cushions, food and people stay
// in the same places in every shot. Original illustration; warm, natural sitcom lighting.
import React from 'react';
import { C } from '../config';

const O = { stroke: C.ink, strokeWidth: 3, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const };

// Couch geometry (world units)
export const COUCH = { x0: 556, x1: 1364, seatY: 690, floorY: 840, cushions: [736, 964, 1192], cw: 228 };
export const SPOT = 0; // Sheldon's spot: the cushion at the viewer's left

export const Background: React.FC<{ frame: number }> = ({ frame }) => (
  <g>
    <defs>
      <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ecd3ab" /><stop offset="1" stopColor="#d9b88b" /></linearGradient>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f3c983" /><stop offset="1" stopColor="#e6926a" /></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#a8754f" /><stop offset="1" stopColor="#8a5c3e" /></linearGradient>
      <radialGradient id="lamp" cx=".5" cy=".5" r=".5"><stop offset="0" stopColor="#fff2c8" stopOpacity=".55" /><stop offset="1" stopColor="#fff2c8" stopOpacity="0" /></radialGradient>
    </defs>
    <rect x={-400} y={-300} width={2720} height={1140} fill="url(#wall)" />
    {/* crown moulding + baseboard */}
    <rect x={-400} y={-300} width={2720} height={330} fill="#e9cfa5" />
    <rect x={-400} y={28} width={2720} height={10} fill="#c9a77c" />
    {/* window with a warm late-afternoon sky */}
    <g>
      <rect x={110} y={170} width={330} height={400} fill="url(#sky)" {...O} />
      {[[130, 420, 60, 150], [200, 380, 50, 190], [260, 450, 70, 120], [340, 400, 55, 170], [400, 460, 40, 110]].map(([x, y, w, h], i) =>
        <rect key={i} x={x} y={y} width={w} height={h} fill="#c97b58" opacity={.75} />)}
      <rect x={110} y={170} width={330} height={400} fill="none" stroke="#f4ead8" strokeWidth={16} />
      <line x1={275} y1={170} x2={275} y2={570} stroke="#f4ead8" strokeWidth={12} />
      <line x1={110} y1={370} x2={440} y2={370} stroke="#f4ead8" strokeWidth={12} />
      <rect x={96} y={570} width={358} height={22} fill="#efe3cd" {...O} />
    </g>
    {/* framed print above the couch: an atom diagram */}
    <g>
      <rect x={830} y={250} width={260} height={200} fill="#f4ead8" {...O} />
      <rect x={848} y={268} width={224} height={164} fill={C.navy} />
      {[0, 60, 120].map(a => <ellipse key={a} cx={960} cy={350} rx={84} ry={28} fill="none" stroke={C.gold} strokeWidth={4} transform={`rotate(${a} 960 350)`} />)}
      <circle cx={960} cy={350} r={10} fill={C.red} />
    </g>
    {/* floor lamp left of the couch */}
    <g>
      <circle cx={505} cy={330} r={170} fill="url(#lamp)" />
      <line x1={505} y1={360} x2={505} y2={840} stroke="#4a3a30" strokeWidth={8} />
      <path d="M450 360 L560 360 L535 280 L475 280 Z" fill="#f2dfb8" {...O} />
      <ellipse cx={505} cy={842} rx={40} ry={8} fill="#4a3a30" />
    </g>
    {/* whiteboard on an easel, right of the couch */}
    <g>
      <line x1={1400} y1={760} x2={1440} y2={300} stroke="#7a6a5a" strokeWidth={8} />
      <line x1={1560} y1={760} x2={1520} y2={300} stroke="#7a6a5a" strokeWidth={8} />
      <rect x={1375} y={250} width={210} height={300} fill="#fbfaf6" {...O} />
      {['E = mc²', '∇·E = ρ/ε₀', 'ψ(x,t)', 'Σ F = ma'].map((s, i) =>
        <text key={i} x={1392} y={300 + i * 60} fontFamily="Inter" fontWeight={600} fontSize={28} fill={i % 2 ? C.blue : '#3a3a3a'}>{s}</text>)}
    </g>
    {/* door, standing open into the hallway */}
    <g>
      <rect x={1610} y={250} width={220} height={600} fill="#5b4031" {...O} />
      <rect x={1622} y={262} width={196} height={588} fill="#3f2c22" />
      <path d="M1830 250 L1900 220 L1900 880 L1830 850 Z" fill="#b07a52" {...O} />
      <circle cx={1888} cy={560} r={7} fill={C.gold} stroke={C.ink} strokeWidth={2} />
      <text x={1712} y={232} textAnchor="middle" fontFamily="Inter" fontWeight={800} fontSize={30} fill="#7a5a3a">4A</text>
    </g>
    {/* floor */}
    <rect x={-400} y={830} width={2720} height={400} fill="url(#floor)" />
    {Array.from({ length: 14 }, (_, i) => <line key={i} x1={-400} y1={850 + i * 22 + i * i * 1.5} x2={2320} y2={850 + i * 22 + i * i * 1.5} stroke="#7c5236" strokeWidth={2} opacity={.5} />)}
    <rect x={-400} y={826} width={2720} height={10} fill="#b48a62" />
  </g>
);

const Cushion: React.FC<{ cx: number; y: number; w: number; h: number; fill: string; dx?: number; rot?: number }> = ({ cx, y, w, h, fill, dx = 0, rot = 0 }) => (
  <g transform={`translate(${dx} 0) rotate(${rot} ${cx} ${y + h / 2})`}>
    <rect x={cx - w / 2} y={y} width={w} height={h} rx={22} fill={fill} {...O} />
    <path d={`M${cx - w / 2 + 16} ${y + h * .62} Q${cx} ${y + h * .78} ${cx + w / 2 - 16} ${y + h * .62}`} fill="none" stroke="#6a4129" strokeWidth={3} opacity={.5} />
  </g>
);

// spot: displacement of Sheldon's seat cushion (0 = aligned, 1 = shoved aside for the food)
export const Couch: React.FC<{ spotShift: number; squash?: number[] }> = ({ spotShift, squash = [0, 0, 0] }) => {
  const { cushions, cw } = COUCH;
  return (
    <g>
      <rect x={590} y={505} width={740} height={210} rx={34} fill="#7e5034" {...O} />
      {cushions.map((cx, i) => <Cushion key={'b' + i} cx={cx} y={528} w={cw - 8} h={170} fill="#94603f" rot={i === SPOT ? -2 * spotShift : 0} dx={i === SPOT ? -10 * spotShift : 0} />)}
      <rect x={600} y={720} width={720} height={112} rx={14} fill="#6f452d" {...O} />
      {cushions.map((cx, i) => (
        <Cushion key={'s' + i} cx={cx} y={672 + squash[i] * 10} w={cw - 4} h={64 - squash[i] * 8} fill="#a36d49"
          dx={i === SPOT ? -34 * spotShift : 0} rot={i === SPOT ? -7 * spotShift : 0} />
      ))}
      <rect x={548} y={590} width={84} height={240} rx={34} fill="#86553a" {...O} />
      <rect x={1288} y={590} width={84} height={240} rx={34} fill="#86553a" {...O} />
      {[600, 1300].map(x => <rect key={x} x={x} y={832} width={22} height={14} fill="#3f2a1e" />)}
    </g>
  );
};

export const TakeoutBox: React.FC<{ x: number; y: number; s?: number; open?: boolean }> = ({ x, y, s = 1, open }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M-44 -50 L44 -50 L34 0 L-34 0 Z" fill="#f4f1ea" {...O} />
    {open ? <path d="M-44 -50 L-56 -84 L56 -84 L44 -50" fill="#ebe6dc" {...O} /> : <path d="M-44 -50 L0 -66 L44 -50" fill="#ebe6dc" {...O} />}
    {open && <path d="M-36 -52 Q-10 -70 20 -56 Q34 -60 38 -52" fill="#d9a441" stroke={C.ink} strokeWidth={2} />}
    <path d="M-20 -58 Q0 -92 20 -58" fill="none" stroke="#8a8a8a" strokeWidth={3} />
    <path d="M-8 -30 l6 -8 l6 8" fill="none" stroke={C.red} strokeWidth={3} />
  </g>
);
// fries carton, origin at the carton's bottom centre
export const Fries: React.FC<{ x: number; y: number; s?: number; rot?: number; count?: number }> = ({ x, y, s = 1, rot = 0, count = 7 }) => (
  <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
    {Array.from({ length: count }, (_, i) => <rect key={i} x={-26 + i * 8} y={-74 - (i % 3) * 10} width={9} height={52} rx={2} fill={C.gold} stroke="#b07c1a" strokeWidth={2} transform={`rotate(${(i - 3) * 4} ${-22 + i * 8} -30)`} />)}
    <path d="M-32 -44 L32 -44 L24 0 L-24 0 Z" fill={C.red} {...O} />
    <path d="M-32 -44 Q0 -30 32 -44" fill="none" stroke={C.ink} strokeWidth={3} />
  </g>
);
export const Fry: React.FC<{ x: number; y: number; rot?: number; s?: number }> = ({ x, y, rot = 0, s = 1 }) => (
  <rect x={-4.5} y={-28} width={9} height={52} rx={2} fill={C.gold} stroke="#b07c1a" strokeWidth={2} transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`} />
);
export const PaperBag: React.FC<{ x: number; y: number; s?: number; rot?: number }> = ({ x, y, s = 1, rot = 0 }) => (
  <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
    <path d="M-34 0 L34 0 L38 -86 L-38 -86 Z" fill="#c9a06a" {...O} />
    <path d="M-38 -86 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l4 10" fill="none" stroke={C.ink} strokeWidth={2.5} />
    <rect x={-16} y={-56} width={32} height={20} rx={4} fill="#f2e4c4" stroke={C.ink} strokeWidth={2} />
  </g>
);
export const Drink: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`}>
    <path d="M-16 -60 L16 -60 L12 0 L-12 0 Z" fill="#f4f1ea" {...O} />
    <rect x={-18} y={-66} width={36} height={8} rx={3} fill="#e9e4da" {...O} />
    <line x1={6} y1={-66} x2={14} y2={-96} stroke={C.red} strokeWidth={5} />
  </g>
);

export const CoffeeTable: React.FC<{ foodOnTable?: boolean }> = ({ foodOnTable }) => (
  <g>
    <ellipse cx={960} cy={1000} rx={560} ry={70} fill="#7a3f33" opacity={.9} />
    <ellipse cx={960} cy={1000} rx={500} ry={56} fill="none" stroke={C.gold} strokeWidth={4} opacity={.5} />
    <path d="M740 900 L1180 900 L1210 930 L710 930 Z" fill="#8a5a3a" {...O} />
    <rect x={710} y={930} width={500} height={24} fill="#6e452d" {...O} />
    {[730, 1170].map(x => <rect key={x} x={x} y={954} width={22} height={52} fill="#5a3826" {...O} />)}
    <Drink x={1100} y={918} />
    {foodOnTable && <><TakeoutBox x={840} y={922} s={.8} /><TakeoutBox x={930} y={924} s={.75} /></>}
  </g>
);
