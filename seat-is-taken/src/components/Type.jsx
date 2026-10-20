// Reusable kinetic typography: phrase reveals, name labels, speech bubbles, highlights, diagram labels, titles.
import React from 'react';
import { interpolate, Easing } from 'remotion';
import { C, FONT } from '../config';

const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const reveal = (f, start, dur = 9) => interpolate(f, [start, start + dur], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });

// A phrase that slides in horizontally and settles; optional mask wipe.
export function Phrase({ f, at, children, dx = 40, style, mask = false }) {
  const k = reveal(f, at);
  return (
    <div style={{ opacity: k, transform: `translateX(${(1 - k) * dx}px)`, clipPath: mask ? `inset(0 ${(1 - k) * 100}% 0 0)` : undefined, ...style }}>{children}</div>
  );
}

export const Hi = ({ children, color = C.red, style }) => <span style={{ color, ...style }}>{children}</span>;

// Underline that draws itself under a keyword.
export const Underline = ({ f, at, width, color = C.red, h = 10, dur = 10 }) => (
  <div style={{ height: h, width: width * reveal(f, at, dur), background: color, borderRadius: h / 2, marginTop: 6 }} />
);

export function NameLabel({ f, at, name, color }) {
  const k = reveal(f, at, 7);
  return (
    <div style={{ display: 'inline-block', background: color, color: C.white, fontFamily: FONT.head, fontSize: 36, letterSpacing: 2, padding: '4px 18px 2px', borderRadius: 8, transform: `scale(${0.8 + 0.2 * k})`, transformOrigin: 'left bottom', opacity: k }}>
      {name}
    </div>
  );
}

// Speech bubble with a tail. tail: 'left' | 'down-left'. Children are Phrase lines.
export function Bubble({ f, at, x, y, w, name, nameColor, tail = 'left', children, pad = 34 }) {
  const k = reveal(f, at, 10);
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: w, transform: `translateX(${(1 - k) * 50}px) scale(${0.96 + 0.04 * k})`, opacity: k, transformOrigin: 'left center' }}>
      {name && <div style={{ position: 'absolute', top: -46, left: 22 }}><NameLabel f={f} at={at + 2} name={name} color={nameColor} /></div>}
      <div style={{ background: C.white, borderRadius: 30, padding: `${pad - 6}px ${pad}px ${pad}px`, boxShadow: `0 8px 0 rgba(38,38,38,0.12)`, fontFamily: FONT.body, fontWeight: 600, color: C.charcoal, fontSize: 52, lineHeight: 1.12 }}>
        {children}
      </div>
      <svg width="70" height="60" style={{ position: 'absolute', ...(tail === 'left' ? { left: -42, top: 70 } : { left: 60, bottom: -46 }) }}>
        {tail === 'left' ? <path d="M70,0 L0,34 L70,52 Z" fill={C.white} /> : <path d="M0,0 L60,0 L10,56 Z" fill={C.white} />}
      </svg>
    </div>
  );
}

export function DiagramLabel({ f, at, children, color = C.blue, style }) {
  const k = reveal(f, at, 8);
  return (
    <div style={{ position: 'absolute', fontFamily: FONT.head, fontSize: 34, letterSpacing: 1.5, color: C.white, background: color, padding: '4px 16px 2px', borderRadius: 6, opacity: k, transform: `translateY(${(1 - k) * 10}px)`, ...style }}>{children}</div>
  );
}

export function Title({ f, at, size = 150 }) {
  const k1 = reveal(f, at, 10), k2 = reveal(f, at + 5, 10), k3 = reveal(f, at + 10, 10);
  const word = (txt, k, extra = {}) => <span style={{ display: 'inline-block', opacity: k, transform: `translateY(${(1 - k) * 24}px)`, ...extra }}>{txt}</span>;
  return (
    <div style={{ fontFamily: FONT.head, fontSize: size, color: C.charcoal, letterSpacing: 2, lineHeight: 1, textAlign: 'center' }}>
      {word('THE ', k1)}
      {word('SEAT', k2, { background: C.red, color: C.white, padding: '0 22px', margin: '0 14px', borderRadius: 6 })}
      {word(' IS TAKEN', k3)}
      <div style={{ height: 10, width: 520 * reveal(f, at + 16, 12), background: C.blue, margin: '22px auto 0', borderRadius: 5 }} />
    </div>
  );
}
