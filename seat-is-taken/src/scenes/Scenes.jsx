// The eight shots. Each scene receives the frame local to its own Sequence.
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { C, FONT, STAGE, SEATS, SHOTS, VO } from '../config';
import { Person, Defs } from '../components/Characters';
import { Couch, Door, Carton, Fry, CouchIcon, Arrow } from '../components/Props';
import { Phrase, Hi, Underline, Bubble, NameLabel, DiagramLabel, Title, reveal } from '../components/Type';

const io = (f, a, b, from, to, easing = Easing.bezier(0.33, 0, 0.2, 1)) => interpolate(f, [a, b], [from, to], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing });
const Stage = ({ children, overlay }) => (
  <AbsoluteFill style={{ background: C.mustard }}>
    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{ position: 'absolute' }}>
      <Defs />
      <rect x="0" y={STAGE.floor} width="1920" height={1080 - STAGE.floor} fill="#F2A532" />
      {children}
    </svg>
    {overlay}
  </AbsoluteFill>
);
const local = (shot, abs) => abs - SHOTS[shot][0]; // convert an absolute frame cue to scene-local
const LEONARD_X = 1010, CARTON_X = 790, CUSHION_MOVED = 70;
const handAt = (x, y, side, deg, len = 236) => [x + side * 122 + side * Math.sin((deg * Math.PI) / 180) * (len + 4), y - 252 + Math.cos((deg * Math.PI) / 180) * (len + 4)];
const head = (px, extra = {}) => ({ fontFamily: FONT.head, fontSize: px, lineHeight: 1.02, letterSpacing: 1, color: C.charcoal, ...extra });
const body = (px, extra = {}) => ({ fontFamily: FONT.body, fontWeight: 600, fontSize: px, lineHeight: 1.15, color: C.charcoal, ...extra });

// 01 THE ARRIVAL
export function Arrival() {
  const f = useCurrentFrame(); const v = (abs) => local('arrival', abs);
  const doorIn = io(f, 0, 12, -420, 0), open = io(f, 4, 20, 0, 1);
  const walk = io(f, 12, 42, 300, 640), moving = f > 12 && f < 42;
  const bob = moving ? Math.abs(Math.sin(f * 0.5)) * -8 : 0, swing = moving ? Math.sin(f * 0.5) * 10 : 0;
  const dip = interpolate(f, [42, 47, 56], [0, 12, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }); // bag settles
  const hip = STAGE.floor - 304;
  return (
    <Stage overlay={
      <div style={{ position: 'absolute', left: 1060, top: 210, width: 780 }}>
        <Phrase f={f} at={8} style={head(66, { color: C.charcoal })}>EVERYTHING HAS ITS PLACE.</Phrase>
        <div style={{ height: 28 }} />
        <Phrase f={f} at={v(VO.narrator.from)} style={body(58)}>For Sheldon Cooper,</Phrase>
        <Phrase f={f} at={v(VO.narrator.from) + 34} style={body(58)}>even a couch has</Phrase>
        <Phrase f={f} at={v(VO.narrator.from) + 67} style={head(230, { color: C.red, marginTop: 6 })}>RULES.</Phrase>
        <Underline f={f} at={v(VO.narrator.from) + 72} width={470} />
      </div>}>
      <g transform={`translate(${doorIn},0)`}><Door x={150} open={open} /></g>
      <CouchIcon x={900} y={790} s={io(f, 30, 42, 0.6, 1)} op={io(f, 30, 40, 0, 1)} />
      <g opacity={io(f, 10, 16, 0, 1)}>
        <Person who="sheldon" x={walk} y={hip + bob} armL={4 + swing} armR={6} />
        <Carton x={handAt(walk, hip + bob, 1, 6)[0]} y={handAt(walk, hip + bob, 1, 6)[1] + 78 + dip} s={0.9} />
      </g>
    </Stage>
  );
}

const SeatedScene = ({ f, cushionDx, leonard = {}, carton = {}, penny, children, overlay, compress = 0 }) => (
  <Stage overlay={overlay}>
    <Couch cushionDx={cushionDx} compress={compress} />
    {penny}
    <Carton x={CARTON_X + (carton.dx || 0)} y={STAGE.seatY - 34} s={0.95} open={carton.open} />
    <Person who="leonard" x={LEONARD_X} y={STAGE.seatY} pose="sit" armL={leonard.armL ?? 8} armR={6} tilt={leonard.tilt || 0} breathe={Math.sin(f * 0.2) * 0.004} />
    {children}
  </Stage>
);

// 02 THE VIOLATION
export function Violation() {
  const f = useCurrentFrame(); const at = local('violation', VO.sheldon1.from);
  const cx0 = STAGE.couchX - STAGE.couchW / 2 + 140, cy0 = STAGE.seatY - 140;
  const dx = io(f, 0, 10, 0, CUSHION_MOVED);
  const tgt = [cx0 + CUSHION_MOVED + 95, cy0 + 64];
  return (
    <SeatedScene f={f} cushionDx={dx} carton={{ open: true }} overlay={
      <Bubble f={f} at={at} x={1350} y={300} w={500} name="SHELDON" nameColor={C.blue} tail="down-left">
        <Phrase f={f} at={at}>Why have you</Phrase>
        <Phrase f={f} at={at + 12}><Hi style={{ fontFamily: FONT.head, fontSize: 84, fontWeight: 400 }}>MOVED</Hi> it?</Phrase>
      </Bubble>}>
      <Arrow x1={tgt[0] - 60} y1={tgt[1] - 250} x2={tgt[0] - 8} y2={tgt[1] - 90} k={reveal(f, 6, 8)} />
      <Arrow x1={tgt[0] - 300} y1={tgt[1] - 60} x2={tgt[0] - 140} y2={tgt[1] - 10} k={reveal(f, 10, 8)} />
      <path d={`M${cx0},${cy0 - 30} L${cx0 + CUSHION_MOVED},${cy0 - 30}`} stroke={C.red} strokeWidth="5" strokeDasharray="10 10" opacity={io(f, 12, 18, 0, 1)} />
    </SeatedScene>
  );
}

// 03 THE EXPLANATION
export function Explanation() {
  const f = useCurrentFrame(); const at = local('explanation', VO.leonard1.from);
  return (
    <SeatedScene f={f} cushionDx={CUSHION_MOVED} leonard={{ armL: io(f, 3, 13, 8, 26) }} carton={{ dx: io(f, 8, 18, 0, -22), open: true }} overlay={
      <Bubble f={f} at={at} x={1350} y={270} w={500} name="LEONARD" nameColor={C.red} tail="down-left">
        <Phrase f={f} at={at}>I needed</Phrase>
        <Phrase f={f} at={at + 14}>space for</Phrase>
        <Phrase f={f} at={at + 33}>the <Hi style={{ fontFamily: FONT.head, fontSize: 88, fontWeight: 400 }}>FOOD.</Hi></Phrase>
      </Bubble>} />
  );
}

// 04 THE LOGIC
export function Logic() {
  const f = useCurrentFrame(); const at = local('logic', VO.sheldon2.from);
  const d = (a, b) => 1 - reveal(f, a, b - a); // dash offset for self-drawing lines
  const L = { strokeLinecap: 'round', strokeLinejoin: 'round', fill: 'none' };
  const X0 = 820, Y0 = 250, Wd = 900; // diagram frame
  const cw = (Wd - 160) / 3;
  return (
    <Stage overlay={<>
      <DiagramLabel f={f} at={4} style={{ left: X0, top: 112 }}>OPTIMAL SEATING COORDINATES</DiagramLabel>
      <DiagramLabel f={f} at={30} color={C.charcoal} style={{ left: X0 + 340, top: Y0 - 64, fontSize: 30 }}>72 CM</DiagramLabel>
      <DiagramLabel f={f} at={36} color={C.charcoal} style={{ left: X0 + Wd + 24, top: Y0 + 200, fontSize: 30 }}>45 CM</DiagramLabel>
      <DiagramLabel f={f} at={42} color={C.gold} style={{ left: X0 + 70, top: Y0 + 300, fontSize: 30, color: C.charcoal }}>(0, 0)</DiagramLabel>
      <div style={{ position: 'absolute', left: X0, top: 640 }}>
        <div style={{ marginBottom: 12 }}><NameLabel f={f} at={at - 2} name="SHELDON" color={C.blue} /></div>
        <Phrase f={f} at={at} style={head(86)}>THE SEATING ARRANGEMENT</Phrase>
        <Phrase f={f} at={at + 37} style={head(86)}>FOLLOWS A</Phrase>
        <Phrase f={f} at={at + 48} style={head(86, { color: C.red })}>SPECIFIC GEOMETRY.</Phrase>
      </div>
    </>}>
      <Person who="sheldon" x={io(f, 0, 12, 120, 380)} y={STAGE.floor - 304} armL={4} armR={io(f, 12, 22, 6, 78)} />
      {/* diagram: a flat explanatory drawing */}
      <g stroke={C.blue} strokeWidth="7" {...L}>
        <path pathLength="1" strokeDasharray="1" strokeDashoffset={d(6, 26)} d={`M${X0 + 40},${Y0 + 260} L${X0 + 40},${Y0 + 60} Q${X0 + 40},${Y0 + 30} ${X0 + 70},${Y0 + 30} L${X0 + Wd - 70},${Y0 + 30} Q${X0 + Wd - 40},${Y0 + 30} ${X0 + Wd - 40},${Y0 + 60} L${X0 + Wd - 40},${Y0 + 260}`} />
        <path pathLength="1" strokeDasharray="1" strokeDashoffset={d(12, 30)} d={`M${X0},${Y0 + 300} L${X0},${Y0 + 150} Q${X0},${Y0 + 130} ${X0 + 20},${Y0 + 130} Q${X0 + 40},${Y0 + 130} ${X0 + 40},${Y0 + 150} L${X0 + 40},${Y0 + 200} L${X0 + Wd - 40},${Y0 + 200} L${X0 + Wd - 40},${Y0 + 150} Q${X0 + Wd - 40},${Y0 + 130} ${X0 + Wd - 20},${Y0 + 130} Q${X0 + Wd},${Y0 + 130} ${X0 + Wd},${Y0 + 150} L${X0 + Wd},${Y0 + 300} Z`} />
        {[1, 2].map((i) => <path key={i} pathLength="1" strokeDasharray="1" strokeDashoffset={d(20 + i * 3, 30 + i * 3)} d={`M${X0 + 80 + i * cw},${Y0 + 200} L${X0 + 80 + i * cw},${Y0 + 300}`} />)}
      </g>
      <rect x={X0 + 86 + cw} y={Y0 + 208} width={cw - 12} height={84} rx={8} fill={C.red} opacity={0.85 * io(f, 30, 38, 0, 1)} />
      <g stroke={C.blue} strokeWidth="4" {...L} opacity={io(f, 26, 32, 0, 1)}>
        <path d={`M${X0 + 80 + cw},${Y0 - 10} L${X0 + 80 + 2 * cw},${Y0 - 10} M${X0 + 80 + cw},${Y0 - 24} L${X0 + 80 + cw},${Y0 + 4} M${X0 + 80 + 2 * cw},${Y0 - 24} L${X0 + 80 + 2 * cw},${Y0 + 4}`} />
        <path d={`M${X0 + Wd + 14},${Y0 + 200} L${X0 + Wd + 14},${Y0 + 300} M${X0 + Wd},${Y0 + 200} L${X0 + Wd + 28},${Y0 + 200} M${X0 + Wd},${Y0 + 300} L${X0 + Wd + 28},${Y0 + 300}`} />
      </g>
      <Arrow x1={X0 + 80 + 1.5 * cw} y1={Y0 + 70} x2={X0 + 80 + 1.5 * cw} y2={Y0 + 190} k={reveal(f, 32, 8)} w={7} />
      {/* gold marker: Sheldon's designated spot */}
      <g transform={`translate(${X0 + 80 + cw / 2},${Y0 + 250}) scale(${io(f, 40, 48, 0, 1, Easing.bezier(0.3, 1.6, 0.5, 1))})`}>
        <circle r="30" fill={C.gold} stroke={C.charcoal} strokeWidth="4" />
        <path d="M0,-16 L5,-5 L17,-5 L7,3 L11,15 L0,8 L-11,15 L-7,3 L-17,-5 L-5,-5 Z" fill={C.charcoal} />
      </g>
    </Stage>
  );
}

// 05 PENNY ARRIVES
export function PennyArrives() {
  const f = useCurrentFrame(); const at = local('penny', VO.penny1.from);
  const px = STAGE.couchX + SEATS.left;
  const sat = f >= 12;
  const x = io(f, 0, 11, -160, px), drop = io(f, 12, 16, -18, 0);
  const comp = interpolate(f, [12, 16, 24], [0, 1, 0.4], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <SeatedScene f={f} cushionDx={CUSHION_MOVED} compress={comp} carton={{ open: true }}
      penny={sat ? <Person who="penny" x={px} y={STAGE.seatY + drop} pose="sit" armL={6} armR={10} /> : <Person who="penny" x={x} y={STAGE.floor - 304 + Math.abs(Math.sin(f * 0.6)) * -6} armL={6 + Math.sin(f * 0.6) * 8} armR={6} />}
      overlay={<Bubble f={f} at={at} x={1350} y={330} w={440} name="PENNY" nameColor={C.teal} tail="down-left"><Phrase f={f} at={at}>Looks comfy.</Phrase></Bubble>} />
  );
}

// 06 THE FRIES
export function Fries() {
  const f = useCurrentFrame();
  const px = STAGE.couchX + SEATS.left;
  const reach = interpolate(f, [0, 7, 14, 20], [10, 58, 58, 18], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const k = io(f, 8, 20, 0, 1);
  const hand = handAt(px, STAGE.seatY, 1, reach);
  const from = [CARTON_X, STAGE.seatY - 128];
  const fx = from[0] + (hand[0] - from[0]) * k, fy = from[1] + (hand[1] - from[1]) * k - Math.sin(k * Math.PI) * 60;
  return (
    <SeatedScene f={f} cushionDx={CUSHION_MOVED} leonard={{ tilt: io(f, 10, 18, 0, -6) }} carton={{ open: true }}
      penny={<Person who="penny" x={px} y={STAGE.seatY} pose="sit" armL={6} armR={reach} />}
      overlay={
        <div style={{ position: 'absolute', left: 1250, top: 210, transform: 'rotate(-4deg)' }}>
          <Phrase f={f} at={2} style={head(130)}>TAKES THE</Phrase>
          <Phrase f={f} at={9} style={head(170, { color: C.red })}>FRIES</Phrase>
        </div>}>
      {f >= 8 && f < 28 && <Fry x={fx} y={fy} rot={k * 60} />}
      <g opacity={io(f, 9, 12, 0, 1) * io(f, 20, 26, 1, 0)} stroke={C.charcoal} strokeWidth="7" strokeLinecap="round">
        {[[-30, -60], [0, -72], [30, -60]].map(([dx, dy], i) => <line key={i} x1={LEONARD_X + dx * 1.2} y1={STAGE.seatY - 300 + dy} x2={LEONARD_X + dx * 1.6} y2={STAGE.seatY - 300 + dy * 1.5} />)}
      </g>
    </SeatedScene>
  );
}

// 07 THE REACTION
export function Reaction() {
  const f = useCurrentFrame(); const at = local('reaction', VO.sheldon3.from);
  return (
    <Stage overlay={
      <Bubble f={f} at={at} x={930} y={210} w={860} name="SHELDON" nameColor={C.blue} tail="left" pad={44}>
        <Phrase f={f} at={at} style={{ fontSize: 66 }}>This is precisely</Phrase>
        <Phrase f={f} at={at + 29} style={{ fontSize: 66 }}>why we need</Phrase>
        <Phrase f={f} at={at + 46} style={head(250, { color: C.red, marginTop: 4 })}>RULES.</Phrase>
      </Bubble>}>
      <Person who="sheldon" x={io(f, 0, 12, 380, 600)} y={STAGE.floor - 304} armL={io(f, 4, 12, 4, 22)} armR={io(f, 4, 12, 6, 22)} />
      <g stroke={C.charcoal} strokeWidth="7" strokeLinecap="round" opacity={io(f, 46, 50, 0, 1)}>
        <line x1={760} y1={250} x2={790} y2={225} /><line x1={772} y1={290} x2={810} y2={286} />
      </g>
    </Stage>
  );
}

// 08 THE HOLD
export function Hold() {
  const f = useCurrentFrame();
  const order = ['extraA', 'leonard', 'penny', 'sheldon', 'extraB'];
  const s = 0.74, cx = 960, gx = cx * (1 - s), gy = 762 - STAGE.floor * s; // couch floor lands at y=762
  const rise = io(f, 0, 12, 40, 0);
  return (
    <Stage overlay={<div style={{ position: 'absolute', left: 0, right: 0, top: 812 }}><Title f={f} at={6} size={150} /></div>}>
      <g transform={`translate(${gx},${gy + rise}) scale(${s})`} opacity={io(f, 0, 8, 0, 1)}>
        <Couch cx={cx} w={1700} seats={4} cushionDx={0} />
        {order.map((who, i) => (
          <Person key={who} who={who} x={cx + (i - 2) * 300} y={STAGE.seatY} pose="sit" armL={6} armR={6}
            breathe={Math.sin(f * 0.25 + i) * 0.006} footTap={who === 'penny' ? Math.max(0, Math.sin(f * 0.5)) * 8 : 0} tilt={who === 'sheldon' ? Math.sin(f * 0.15) * 0.6 : 0} />
        ))}
      </g>
    </Stage>
  );
}
