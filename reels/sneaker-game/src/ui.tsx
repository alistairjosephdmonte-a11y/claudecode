import React, { createContext, useContext } from "react";
import { Audio, Easing, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import voice from "./voice.json";

export const FPS = 30;
export const C = {
  ink: "#141414",
  blue: "#3B62DB",
  soft: "#EAF0FD",
  muted: "#8A8A8A",
  line: "#E6E6E6",
};
export const SANS = "Manrope";
export const SERIF = "Instrument Serif";

const fontFaces = `
@font-face{font-family:Manrope;font-weight:600;src:url(${staticFile("fonts/manrope-latin-600-normal.woff2")}) format("woff2")}
@font-face{font-family:Manrope;font-weight:700;src:url(${staticFile("fonts/manrope-latin-700-normal.woff2")}) format("woff2")}
@font-face{font-family:Manrope;font-weight:800;src:url(${staticFile("fonts/manrope-latin-800-normal.woff2")}) format("woff2")}
@font-face{font-family:"Instrument Serif";font-style:italic;font-weight:400;src:url(${staticFile("fonts/instrument-serif-latin-400-italic.woff2")}) format("woff2")}
`;
export const Fonts: React.FC = () => <style>{fontFaces}</style>;

export const f = (s: number) => Math.round(s * FPS);
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

export const lineStart = (line: number) => f(voice.lines[line].start);

export const at = (line: number, word: string) => {
  const w = voice.words.find((x) => x.line === line && norm(x.text).startsWith(norm(word)));
  if (!w) throw new Error(`word "${word}" not found in line ${line}`);
  return f(w.start);
};

const SceneFrom = createContext(0);
export const SceneFromProvider = SceneFrom.Provider;

export const useAbsFrame = () => useCurrentFrame() + useContext(SceneFrom);

const ease = Easing.bezier(0.16, 1, 0.3, 1);

export const useIn = (start: number, dur = 16) => {
  const frame = useAbsFrame();
  return interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
};

export const Sfx: React.FC<{ at: number; type?: "pop" | "tick" | "confirm"; volume?: number }> = ({
  at: a,
  type = "pop",
  volume = 0.12,
}) => {
  const from = useContext(SceneFrom);
  return (
    <Sequence from={a - from} durationInFrames={15} layout="none">
      <Audio src={staticFile(`${type}.wav`)} volume={volume} />
    </Sequence>
  );
};

export const Pop: React.FC<{ at: number; children: React.ReactNode; y?: number; style?: React.CSSProperties; sfx?: "pop" | "tick" | "confirm" | null }> = ({
  at: a,
  children,
  y = 24,
  style,
  sfx = "pop",
}) => {
  const p = useIn(a);
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * y}px) scale(${0.94 + 0.06 * p})`, ...style }}>
      {sfx && <Sfx at={a} type={sfx} />}
      {children}
    </div>
  );
};

export const Kicker: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: "absolute",
      top: 222,
      left: 90,
      width: 870,
      textAlign: "center",
      fontFamily: SANS,
      fontWeight: 800,
      fontSize: 30,
      letterSpacing: "0.18em",
      color: C.blue,
    }}
  >
    <span style={{ background: C.soft, padding: "12px 26px", borderRadius: 999 }}>{children}</span>
  </div>
);

export const Headline: React.FC<{ top: React.ReactNode; accent: React.ReactNode; accentAt?: number }> = ({
  top,
  accent,
  accentAt,
}) => {
  const p = useIn(accentAt ?? -999);
  return (
    <div style={{ position: "absolute", top: 340, left: 90, width: 870, textAlign: "center", color: C.ink }}>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 92, letterSpacing: "-0.035em", lineHeight: 1.05 }}>
        {top}
      </div>
      <div
        style={{
          fontFamily: SERIF,
          fontStyle: "italic",
          fontSize: 116,
          color: C.blue,
          letterSpacing: "-0.02em",
          lineHeight: 1.05,
          opacity: p,
          transform: `translateY(${(1 - p) * 20}px)`,
        }}
      >
        {accent}
      </div>
    </div>
  );
};

export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: "absolute",
      top: 720,
      left: 90,
      width: 870,
      height: 590,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 28,
    }}
  >
    {children}
  </div>
);

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: "white",
      border: `2px solid ${C.line}`,
      borderRadius: 32,
      boxShadow: "0 18px 40px rgba(20,20,20,0.08), 0 2px 6px rgba(20,20,20,0.05)",
      padding: 32,
      fontFamily: SANS,
      color: C.ink,
      ...style,
    }}
  >
    {children}
  </div>
);

export const Label: React.FC<{ children: React.ReactNode; size?: number; color?: string; weight?: number; style?: React.CSSProperties }> = ({
  children,
  size = 40,
  color = C.ink,
  weight = 700,
  style,
}) => (
  <div style={{ fontFamily: SANS, fontSize: size, fontWeight: weight, color, letterSpacing: "-0.02em", ...style }}>
    {children}
  </div>
);

export const Strike: React.FC<{ at: number; children: React.ReactNode }> = ({ at: a, children }) => {
  const p = useIn(a, 14);
  return (
    <span style={{ position: "relative", display: "inline-block", opacity: 1 - 0.45 * p }}>
      <Sfx at={a} type="tick" />
      {children}
      <span
        style={{
          position: "absolute",
          left: -8,
          top: "52%",
          height: 6,
          borderRadius: 3,
          width: `calc(${p * 100}% + ${p * 16}px)`,
          background: C.blue,
        }}
      />
    </span>
  );
};

export const IconBubble: React.FC<{ children: React.ReactNode; size?: number; filled?: boolean }> = ({
  children,
  size = 110,
  filled,
}) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.3,
      background: filled ? C.blue : C.soft,
      color: filled ? "white" : C.blue,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexShrink: 0,
    }}
  >
    {children}
  </div>
);

export const icon = { strokeWidth: 3, absoluteStrokeWidth: true } as const;

export const Sneaker: React.FC<{ width?: number; laces?: number; color?: string }> = ({
  width = 420,
  laces = 1,
  color = C.ink,
}) => {
  const s = { fill: "none", stroke: color, strokeWidth: 3, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, vectorEffect: "non-scaling-stroke" as const };
  const laceLines = [
    [92, 56, 102, 46],
    [106, 63, 116, 53],
    [120, 68, 130, 58],
  ];
  return (
    <svg width={width} height={width / 2} viewBox="0 0 240 120">
      <path d="M14 92 H226 Q234 92 234 101 Q234 110 224 110 H22 Q10 110 10 101 Q10 92 14 92 Z" {...s} fill={C.soft} />
      <path d="M14 92 L18 50 Q20 36 36 36 L66 36 Q80 36 88 48 L104 64 Q150 70 196 76 Q230 82 230 92" {...s} fill="white" />
      <path d="M36 36 Q40 28 52 28 L64 28 Q74 28 78 36" {...s} />
      <path d="M176 92 Q178 79 196 76" {...s} />
      <path d="M18 70 H60 Q74 70 84 80 L96 92" {...s} stroke={C.blue} />
      {laceLines.map(([x1, y1, x2, y2], i) => {
        const p = Math.max(0, Math.min(1, laces * 3 - i));
        return <line key={i} x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} {...s} />;
      })}
    </svg>
  );
};
