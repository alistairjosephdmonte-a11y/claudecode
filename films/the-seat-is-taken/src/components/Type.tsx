// Reusable typography: name labels, phrase-by-phrase dialogue captions, keyword highlights,
// underline reveals, diagram annotations, lower thirds and titles. All frame-driven (deterministic).
import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';
import { C, FONT } from '../config';

const ease = Easing.bezier(.2, .8, .2, 1);
export const inOut = (f: number, a: number, b: number, fi = 6, fo = 6) =>
  Math.min(interpolate(f, [a, a + fi], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
    interpolate(f, [b - fo, b], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));

export type Token = { t: string; c?: string; scale?: number };
export type Phrase = { at: number; tokens: Token[] };

const base: React.CSSProperties = { fontFamily: FONT, fontWeight: 800, letterSpacing: '0.01em', textTransform: 'uppercase', lineHeight: 1.04, whiteSpace: 'nowrap' };

// A phrase that slides up out of a mask when its frame arrives
export const PhraseLine: React.FC<{ p: Phrase; size: number; color?: string }> = ({ p, size, color = C.white }) => {
  const f = useCurrentFrame();
  const u = interpolate(f, [p.at, p.at + 7], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
  if (f < p.at) return null;
  return (
    <span style={{ display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', paddingBottom: size * .08, marginRight: size * .26 }}>
      <span style={{ display: 'inline-block', transform: `translateY(${(1 - u) * 100}%)` }}>
        {p.tokens.map((k, i) => (
          <span key={i} style={{ color: k.c ?? color, fontSize: size * (k.scale ?? 1), marginRight: i < p.tokens.length - 1 ? size * .26 : 0, display: 'inline-block' }}>{k.t}</span>
        ))}
      </span>
    </span>
  );
};

export const NameLabel: React.FC<{ name: string; at: number }> = ({ name, at }) => {
  const f = useCurrentFrame();
  const u = interpolate(f, [at, at + 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
  return (
    <div style={{ ...base, display: 'inline-block', fontSize: 22, fontWeight: 800, letterSpacing: '0.14em', color: C.white, background: C.blue,
      padding: '7px 14px 6px', borderRadius: 6, marginBottom: 12, opacity: u, transform: `translateX(${(1 - u) * -16}px)` }}>{name}</div>
  );
};

// Dialogue caption: navy panel, speaker label, phrases revealed on their frames
export const Caption: React.FC<{ x: number; y: number; name?: string; phrases: Phrase[]; until: number; size?: number; align?: 'left' | 'right'; maxW?: number; panel?: boolean }> =
  ({ x, y, name, phrases, until, size = 64, align = 'left', maxW = 1100, panel = true }) => {
    const f = useCurrentFrame();
    const from = phrases[0].at - 2;
    const a = inOut(f, from, until, 4, 6);
    if (a <= 0) return null;
    const pu = interpolate(f, [from, from + 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
    return (
      <div style={{ position: 'absolute', left: align === 'left' ? x : undefined, right: align === 'right' ? 1920 - x : undefined, top: y, opacity: a, maxWidth: maxW, textAlign: align }}>
        {name && <NameLabel name={name} at={from} />}
        <div style={{ ...base, fontSize: size, color: C.white, whiteSpace: 'normal', padding: panel ? '16px 26px 12px' : 0, borderRadius: 10,
          background: panel ? `rgba(16,29,53,${.82 * pu})` : 'transparent', boxShadow: panel ? '0 8px 30px rgba(16,29,53,.25)' : undefined }}>
          {phrases.map((p, i) => <PhraseLine key={i} p={p} size={size} />)}
        </div>
      </div>
    );
  };

// Underline that draws left→right
export const Underline: React.FC<{ at: number; color?: string; width: number; thick?: number }> = ({ at, color = C.blue, width, thick = 8 }) => {
  const f = useCurrentFrame();
  const u = interpolate(f, [at, at + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
  return <div style={{ height: thick, width: width * u, background: color, borderRadius: thick }} />;
};

// Lower third: small headline + rule (used for the narrator line in shot 1)
export const LowerThird: React.FC<{ x: number; y: number; small: string; big: string; atSmall: number; atBig: number; until: number; align?: 'left' | 'right' }> =
  ({ x, y, small, big, atSmall, atBig, until, align = 'right' }) => {
    const f = useCurrentFrame();
    const a = inOut(f, atSmall, until, 4, 6);
    if (a <= 0) return null;
    const bigU = interpolate(f, [atBig, atBig + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
    const s = interpolate(f, [atBig, atBig + 5, atBig + 10], [.82, 1.06, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (
      <div style={{ position: 'absolute', left: align === 'left' ? x : undefined, right: align === 'right' ? 1920 - x : undefined, top: y, opacity: a, textAlign: align, display: 'flex', flexDirection: 'column', alignItems: align === 'right' ? 'flex-end' : 'flex-start',
        background: 'rgba(16,29,53,.82)', padding: '16px 26px 20px', borderRadius: 12 }}>
        <div style={{ ...base, fontSize: 34, color: C.white, textShadow: '0 2px 14px rgba(16,29,53,.55)' }}><PhraseLine p={{ at: atSmall, tokens: [{ t: small }] }} size={34} /></div>
        <div style={{ ...base, fontSize: 132, color: C.gold, opacity: bigU, transform: `scale(${s})`, transformOrigin: align === 'right' ? 'right bottom' : 'left bottom', textShadow: '0 4px 24px rgba(16,29,53,.5)' }}>{big}</div>
        <Underline at={atBig + 4} width={250} />
      </div>
    );
  };

// Short single-word / phrase stamp (e.g. TAKES THE FRIES)
export const Stamp: React.FC<{ x: number; y: number; text: string; at: number; until: number; color: string; size?: number }> = ({ x, y, text, at, until, color, size = 74 }) => {
  const f = useCurrentFrame();
  const a = inOut(f, at, until, 3, 5);
  if (a <= 0) return null;
  const s = interpolate(f, [at, at + 4, at + 8], [1.25, .96, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <div style={{ position: 'absolute', left: x, top: y, transform: `translate(-50%, 0) scale(${s})`, opacity: a }}>
      <div style={{ ...base, fontSize: size, color: C.white, background: color, padding: '10px 24px 6px', borderRadius: 8, transform: 'rotate(-2deg)' }}>{text}</div>
    </div>
  );
};

export const Title: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const u = interpolate(f, [at, at + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 906, display: 'flex', justifyContent: 'center', opacity: u }}>
      <div style={{ ...base, fontSize: 58, color: C.white, background: `rgba(16,29,53,.88)`, padding: '14px 34px 10px', borderRadius: 10, letterSpacing: '0.04em', transform: `translateY(${(1 - u) * 18}px)` }}>
        <span style={{ color: C.gold }}>THE SEAT</span> IS TAKEN
      </div>
    </div>
  );
};
