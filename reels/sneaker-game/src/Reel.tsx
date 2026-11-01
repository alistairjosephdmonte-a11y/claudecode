import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import {
  Bookmark,
  Bot,
  Check,
  Coins,
  Crown,
  Dices,
  FileCheck,
  Hourglass,
  Lock,
  MessageCircle,
  Mic,
  Music,
  Package,
  ShieldCheck,
  Smartphone,
  Store,
  Ticket,
  TrendingUp,
  User,
  Users,
} from "lucide-react";
import voice from "./voice.json";
import {
  at,
  C,
  Card,
  f,
  Fonts,
  Headline,
  icon,
  IconBubble,
  Kicker,
  Label,
  lineStart,
  Pop,
  SANS,
  SceneFromProvider,
  SERIF,
  Sfx,
  Sneaker,
  Stage,
  Strike,
  useAbsFrame,
  useIn,
} from "./ui";

const Row: React.FC<{ children: React.ReactNode; gap?: number; style?: React.CSSProperties }> = ({ children, gap = 24, style }) => (
  <div style={{ display: "flex", alignItems: "center", gap, ...style }}>{children}</div>
);

const Hook = () => {
  const flip = at(0, "flip");
  const k = at(0, "thousand");
  const frame = useAbsFrame();
  const price = Math.round(interpolate(frame, [flip, k + 6], [100, 1000], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) / 10) * 10;
  const p = useIn(flip);
  return (
    <>
      <Kicker>THE SNEAKER GAME</Kicker>
      <Headline top="A $100 shoe" accent="can flip for $1,000." />
      <Stage>
        <Card style={{ padding: "40px 56px", display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          <Sneaker width={480} />
          <Row gap={28}>
            <div style={{ border: `3px solid ${C.ink}`, borderRadius: 18, padding: "10px 24px" }}>
              <Label size={26} color={C.muted} weight={800} style={{ letterSpacing: "0.12em" }}>RETAIL</Label>
              <Label size={56} weight={800}>$100</Label>
            </div>
            <div style={{ opacity: p, transform: `translateX(${(1 - p) * -30}px)` }}>
              <TrendingUp size={56} color={C.blue} {...icon} />
            </div>
            <div style={{ opacity: p, background: C.blue, color: "white", borderRadius: 18, padding: "10px 24px" }}>
              <Sfx at={flip} />
              <Sfx at={k} type="confirm" />
              <Label size={26} color="white" weight={800} style={{ letterSpacing: "0.12em", opacity: 0.85 }}>RESALE</Label>
              <Label size={56} color="white" weight={800} style={{ fontVariantNumeric: "tabular-nums" }}>${price.toLocaleString("en-US")}</Label>
            </div>
          </Row>
        </Card>
      </Stage>
    </>
  );
};

const STEPS = [
  { n: 1, t: "The story" },
  { n: 2, t: "The culture" },
  { n: 3, t: "Scarcity" },
  { n: 4, t: "Resale" },
];

const Design = () => {
  const brk = at(2, "break");
  const design = at(1, "design");
  const line = useIn(design, 30);
  return (
    <>
      <Kicker>HOW IT WORKS</Kicker>
      <Headline top="Not luck." accent="By design." accentAt={design} />
      <Stage>
        <Row gap={20}>
          <IconBubble size={84}>
            <Dices size={44} {...icon} />
          </IconBubble>
          <Label size={48}>
            <Strike at={at(1, "luck")}>Luck</Strike>
          </Label>
        </Row>
        <div style={{ position: "relative", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22, width: 800 }}>
          <div style={{ position: "absolute", left: 40, right: 40, top: "50%", height: 4, background: C.blue, transformOrigin: "left", transform: `scaleX(${line})`, borderRadius: 2 }} />
          {STEPS.map((s, i) => {
            const a = brk + i * 6;
            return <StepCard key={s.n} n={s.n} t={s.t} at={a} />;
          })}
        </div>
      </Stage>
    </>
  );
};

const StepCard: React.FC<{ n: number; t: string; at: number }> = ({ n, t, at: a }) => {
  const p = useIn(a);
  return (
    <div
      style={{
        position: "relative",
        borderRadius: 28,
        padding: "26px 28px",
        border: `3px ${p > 0.5 ? "solid" : "dashed"} ${p > 0.5 ? C.line : "#CFCFCF"}`,
        background: "white",
        boxShadow: `0 16px 34px rgba(20,20,20,${0.08 * p})`,
        display: "flex",
        alignItems: "center",
        gap: 20,
      }}
    >
      <Sfx at={a} type="tick" />
      <div style={{ width: 64, height: 64, borderRadius: 20, background: p > 0.5 ? C.blue : C.soft, color: p > 0.5 ? "white" : C.blue, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 800, fontSize: 34 }}>
        {n}
      </div>
      <Label size={40} style={{ opacity: 0.15 + 0.85 * p }}>{t}</Label>
    </div>
  );
};

const Story = () => {
  const yr = at(3, "1985");
  const jordan = at(3, "jordan");
  const hl = useIn(jordan);
  return (
    <>
      <Kicker>STEP 1 · THE STORY</Kicker>
      <Headline top="Step 1:" accent="the story." />
      <Stage>
        <Card style={{ position: "relative", padding: "30px 60px 34px", display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <Pop at={yr} style={{ position: "absolute", top: -26, right: -26 }}>
            <div style={{ background: C.blue, color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 40, padding: "10px 22px", borderRadius: 18 }}>1985</div>
          </Pop>
          <Sneaker width={420} />
          <Label size={52} weight={800} style={{ background: `linear-gradient(${C.soft},${C.soft}) no-repeat 0 85% / ${hl * 100}% 40%` }}>
            Air Jordan 1
          </Label>
        </Card>
        <Row gap={22}>
          <Pop at={at(4, "rookie")}>
            <Card style={{ padding: "18px 26px", display: "flex", alignItems: "center", gap: 16 }}>
              <User size={44} color={C.blue} {...icon} />
              <Label size={34}>Nike signs a rookie · 1984</Label>
            </Card>
          </Pop>
        </Row>
        <Pop at={at(4, "brand")} sfx="confirm">
          <Row gap={14} style={{ background: C.blue, color: "white", padding: "14px 28px", borderRadius: 999 }}>
            <Crown size={40} color="white" {...icon} />
            <Label size={38} color="white" weight={800}>Jordan Brand</Label>
          </Row>
        </Pop>
      </Stage>
    </>
  );
};

const Culture = () => {
  const run = at(5, "run");
  const p = useIn(run);
  return (
    <>
      <Kicker>STEP 2 · THE CULTURE</Kicker>
      <Headline top="Step 2:" accent="the culture." />
      <Stage>
        <Card style={{ width: 760, display: "flex", alignItems: "center", gap: 28 }}>
          <Sfx at={run} />
          <IconBubble size={120} filled={p > 0.5}>
            <Music size={60} {...icon} />
          </IconBubble>
          <div>
            <Label size={54} weight={800} style={{ opacity: 0.2 + 0.8 * p }}>Run-DMC</Label>
            <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 58, color: C.blue, opacity: useIn(at(5, "adidas")) }}>“My Adidas,” 1986</div>
          </div>
        </Card>
        <Row gap={24}>
          <Pop at={at(6, "deal")} sfx="confirm">
            <Sheet title="Sneaker deal">
              <Row gap={12}>
                <FileCheck size={40} color={C.blue} {...icon} />
                <Label size={30} color={C.muted}>Signed</Label>
              </Row>
            </Sheet>
          </Pop>
          <Pop at={at(6, "locked")}>
            <Card style={{ display: "flex", alignItems: "center", gap: 18, padding: "34px 30px" }}>
              <Mic size={52} color={C.ink} {...icon} />
              <Lock size={44} color={C.blue} {...icon} />
              <Sneaker width={150} />
            </Card>
          </Pop>
        </Row>
      </Stage>
    </>
  );
};

const Sheet: React.FC<{ title: string; children: React.ReactNode; width?: number }> = ({ title, children, width = 320 }) => (
  <div style={{ position: "relative", width, background: "white", border: `2px solid ${C.line}`, borderRadius: 18, padding: "28px 30px", boxShadow: "0 18px 40px rgba(20,20,20,0.08)", clipPath: "polygon(0 0, calc(100% - 44px) 0, 100% 44px, 100% 100%, 0 100%)" }}>
    <div style={{ position: "absolute", top: 0, right: 0, width: 44, height: 44, background: C.soft, borderBottomLeftRadius: 10 }} />
    <Label size={34} weight={800} style={{ marginBottom: 14 }}>{title}</Label>
    {children}
  </div>
);

const Bar: React.FC<{ label: string; Icon: typeof Package; at: number; to: number }> = ({ label, Icon, at: a, to }) => {
  const p = useIn(a, 28);
  return (
    <div style={{ width: 780 }}>
      <Sfx at={a} type="tick" />
      <Row gap={16} style={{ marginBottom: 14 }}>
        <Icon size={44} color={C.blue} {...icon} />
        <Label size={40}>{label}</Label>
      </Row>
      <div style={{ height: 56, borderRadius: 18, background: C.soft, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${p * to * 100}%`, background: C.blue, borderRadius: 18 }} />
      </div>
    </div>
  );
};

const Scarcity = () => (
  <>
    <Kicker>STEP 3 · SCARCITY</Kicker>
    <Headline top="Step 3:" accent="scarcity." />
    <Stage>
      <Card style={{ padding: "44px 46px", display: "flex", flexDirection: "column", gap: 44 }}>
        <Bar label="Pairs made" Icon={Package} at={at(7, "fewer")} to={0.22} />
        <Bar label="People who want one" Icon={Users} at={at(7, "want")} to={1} />
      </Card>
    </Stage>
  </>
);

const Lane: React.FC<{ label: string; Icon: typeof Bot; at: number; speed: number }> = ({ label, Icon, at: a, speed }) => {
  const frame = useAbsFrame();
  const p = Math.max(0, Math.min(0.94, ((frame - a) / 45) * speed));
  const shown = useIn(a);
  return (
    <Row gap={20} style={{ width: 800 }}>
      <Sfx at={a} type="tick" />
      <div style={{ width: 210, display: "flex", alignItems: "center", gap: 12, opacity: 0.25 + 0.75 * shown }}>
        <Icon size={44} color={C.blue} {...icon} />
        <Label size={36}>{label}</Label>
      </div>
      <div style={{ position: "relative", flex: 1, height: 18, borderRadius: 9, background: C.line }}>
        <div style={{ height: "100%", width: `${p * 100}%`, background: C.blue, borderRadius: 9 }} />
        <div style={{ position: "absolute", top: -11, left: `calc(${p * 100}% - 20px)`, width: 40, height: 40, borderRadius: 20, background: "white", border: `3px solid ${C.blue}`, opacity: shown }} />
      </div>
    </Row>
  );
};

const DropDay = () => {
  const frame = useAbsFrame();
  const race = at(8, "racing");
  return (
    <>
      <Kicker>DROP DAY</Kicker>
      <Headline top="Drop day:" accent="everyone races." accentAt={race} />
      <Stage>
        <Card style={{ position: "relative", padding: "40px 40px", display: "flex", flexDirection: "column", gap: 44 }}>
          <Lane label="Raffles" Icon={Ticket} at={at(8, "raffles")} speed={0.6} />
          <Lane label="Apps" Icon={Smartphone} at={at(8, "apps")} speed={0.8} />
          <Lane label="Bots" Icon={Bot} at={at(8, "bots")} speed={1.6} />
          <div style={{ position: "absolute", right: 58, top: 30, bottom: 30, borderLeft: `4px dashed ${C.ink}`, opacity: 0.35 }} />
        </Card>
        <Row gap={14}>
          <Package size={44} color={C.ink} {...icon} style={{ transform: `rotate(${Math.sin(frame / 8) * 3}deg)` }} />
          <Label size={36} color={C.muted}>Only so many pairs</Label>
        </Row>
      </Stage>
    </>
  );
};

const FlowNode: React.FC<{ Icon: typeof Store; label: string; on: number; strong?: boolean }> = ({ Icon, label, on, strong }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
    <IconBubble size={strong ? 130 : 104} filled={strong && on > 0.5}>
      <Icon size={strong ? 64 : 52} {...icon} />
    </IconBubble>
    <Label size={32}>{label}</Label>
  </div>
);

const Resale = () => {
  const sx = at(10, "stockx");
  const real = at(10, "real");
  const cut = at(10, "cut");
  const sxp = useIn(sx);
  const cutp = useIn(cut);
  return (
    <>
      <Kicker>STEP 4 · RESALE</Kicker>
      <Headline top="Step 4:" accent="resale." />
      <Stage>
        <Row gap={30}>
          <Card style={{ padding: "20px 30px" }}>
            <Label size={26} color={C.muted} weight={800} style={{ letterSpacing: "0.12em" }}>RETAIL</Label>
            <Label size={44} weight={800}>
              <Strike at={at(9, "miss")}>Sold out</Strike>
            </Label>
          </Card>
          <Pop at={at(9, "market")}>
            <Card style={{ padding: "20px 30px", background: C.blue, border: "none", color: "white" }}>
              <Label size={26} color="white" weight={800} style={{ letterSpacing: "0.12em", opacity: 0.85 }}>MARKET</Label>
              <Row gap={12}>
                <Label size={44} color="white" weight={800}>Higher</Label>
                <TrendingUp size={44} color="white" {...icon} />
              </Row>
            </Card>
          </Pop>
        </Row>
        <Card style={{ position: "relative", width: 800, padding: "34px 30px 60px", display: "flex", alignItems: "center", justifyContent: "space-around" }}>
          <Sfx at={sx} />
          <FlowNode Icon={Store} label="Seller" on={1} />
          <div style={{ flex: 1, height: 4, background: C.line, margin: "0 6px 40px" }} />
          <div style={{ position: "relative", opacity: 0.35 + 0.65 * sxp }}>
            <FlowNode Icon={ShieldCheck} label="StockX" on={sxp} strong />
            <Pop at={real} sfx="confirm" style={{ position: "absolute", top: -14, right: -14 }}>
              <div style={{ width: 52, height: 52, borderRadius: 26, background: "white", border: `3px solid ${C.blue}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Check size={30} color={C.blue} {...icon} />
              </div>
            </Pop>
          </div>
          <div style={{ flex: 1, height: 4, background: C.line, margin: "0 6px 40px" }} />
          <FlowNode Icon={User} label="Buyer" on={1} />
          <div style={{ position: "absolute", bottom: 14, left: "50%", transform: `translate(-50%, ${(1 - cutp) * -30}px)`, opacity: cutp, display: "flex", alignItems: "center", gap: 10 }}>
            <Sfx at={cut} type="tick" />
            <Coins size={34} color={C.blue} {...icon} />
            <Label size={28} color={C.blue} weight={800}>Fee</Label>
          </div>
        </Card>
      </Stage>
    </>
  );
};

const Objection1 = () => {
  const nah = at(12, "nah");
  const lace = useIn(at(12, "lace"), 30);
  return (
    <>
      <Kicker>YOU MIGHT BE THINKING…</Kicker>
      <Headline top="“It's just shoes.”" accent="Nah, it's status." accentAt={nah} />
      <Stage>
        <Card style={{ display: "flex", alignItems: "center", gap: 20, padding: "24px 34px", borderRadius: "32px 32px 32px 8px" }}>
          <MessageCircle size={46} color={C.muted} {...icon} />
          <Label size={46}>
            <Strike at={nah}>It's just shoes.</Strike>
          </Label>
        </Card>
        <Pop at={at(12, "status")} sfx="confirm">
          <Card style={{ position: "relative", padding: "40px 60px 30px", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ position: "absolute", top: -40, left: "50%", transform: "translateX(-50%)" }}>
              <IconBubble size={84} filled>
                <Crown size={46} {...icon} />
              </IconBubble>
            </div>
            <Sneaker width={420} laces={lace} />
            <Label size={40} weight={800}>Status you can lace up</Label>
          </Card>
        </Pop>
      </Stage>
    </>
  );
};

const Objection2 = () => {
  const cow = at(14, "cowen");
  const draw = useIn(cow, 50);
  const len = 760;
  return (
    <>
      <Kicker>OR MAYBE…</Kicker>
      <Headline top="“Resale is" accent="a bubble.”" />
      <Stage>
        <Card style={{ position: "relative", width: 800, height: 520, padding: 0 }}>
          <Row gap={12} style={{ position: "absolute", top: 30, left: 36 }}>
            <Label size={30} color={C.muted} weight={800} style={{ letterSpacing: "0.1em" }}>RESALE MARKET · PROJECTED</Label>
          </Row>
          <svg width={800} height={520} style={{ position: "absolute", inset: 0 }}>
            <line x1={70} y1={440} x2={740} y2={440} stroke={C.line} strokeWidth={3} />
            <line x1={70} y1={110} x2={70} y2={440} stroke={C.line} strokeWidth={3} />
            <path d="M70 420 C 260 405, 420 350, 560 260 S 700 140, 720 130" fill="none" stroke={C.blue} strokeWidth={6} strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - draw)} />
          </svg>
          <Sfx at={cow} type="tick" />
          <Pop at={at(14, "30")} style={{ position: "absolute", top: 120, left: 380 }} sfx="confirm">
            <div style={{ background: C.blue, color: "white", borderRadius: 20, padding: "12px 24px", fontFamily: SANS, fontWeight: 800, fontSize: 52 }}>$30B</div>
          </Pop>
          <Pop at={at(14, "2030")} style={{ position: "absolute", bottom: 26, right: 40 }} sfx="tick">
            <Label size={36} weight={800}>by 2030</Label>
          </Pop>
          <Label size={24} color={C.muted} style={{ position: "absolute", bottom: 30, left: 80 }}>Source: Cowen (projection)</Label>
        </Card>
      </Stage>
    </>
  );
};

const RealProduct = () => {
  const frame = useAbsFrame();
  const wait = at(15, "wait");
  const p = useIn(wait);
  return (
    <>
      <Kicker>THE REAL PRODUCT</Kicker>
      <Headline top="Not the shoe." accent="It's the wait." accentAt={wait} />
      <Stage>
        <Row gap={50}>
          <Card style={{ position: "relative", padding: "30px 34px", opacity: 1 - 0.5 * useIn(at(15, "shoe")) }}>
            <Sneaker width={300} />
            <div style={{ position: "absolute", left: 30, right: 30, top: "50%", height: 6, borderRadius: 3, background: C.blue, transformOrigin: "left", transform: `rotate(-12deg) scaleX(${useIn(at(15, "shoe"), 14)})` }} />
            <Sfx at={at(15, "shoe")} type="tick" />
          </Card>
          <div style={{ width: 260, height: 260, borderRadius: 70, border: `3px ${p > 0.5 ? "solid" : "dashed"} ${p > 0.5 ? C.blue : "#CFCFCF"}`, background: p > 0.5 ? C.soft : "white", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Sfx at={wait} type="confirm" />
            <div style={{ opacity: p, transform: `scale(${0.8 + 0.2 * p}) rotate(${interpolate(frame, [wait + 6, wait + 30], [0, 180], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}deg)` }}>
              <Hourglass size={150} color={C.blue} {...icon} />
            </div>
          </div>
        </Row>
      </Stage>
    </>
  );
};

const CHECK = ["Set reminders", "Enter every raffle", "Save your payment info", "Check retail first"];

const Cta = () => {
  const frame = useAbsFrame();
  const kicks = at(16, "kicks");
  const typed = Math.max(0, Math.min(5, Math.floor((frame - kicks) / 2)));
  const list = at(16, "checklist");
  return (
    <>
      <Kicker>FREE CHECKLIST</Kicker>
      <Headline top="Comment" accent="KICKS." accentAt={kicks} />
      <Stage>
        <Card style={{ width: 760, padding: "22px 28px", display: "flex", alignItems: "center", gap: 18 }}>
          <MessageCircle size={44} color={C.muted} {...icon} />
          <Label size={44} weight={800} style={{ color: typed ? C.blue : C.muted }}>
            {typed ? "KICKS".slice(0, typed) : "Add a comment…"}
            <span style={{ opacity: typed && typed < 5 ? 1 : 0.5 + 0.5 * Math.cos(frame / 6), color: C.blue }}>|</span>
          </Label>
          {[0, 1, 2, 3, 4].map((i) => (
            <Sfx key={i} at={kicks + i * 2} type="tick" volume={0.08} />
          ))}
        </Card>
        <Row gap={28} style={{ alignItems: "flex-start" }}>
          <Sheet title="Drop-day checklist" width={500}>
            {CHECK.map((c, i) => (
              <CheckItem key={c} text={c} at={list + 4 + i * 6} />
            ))}
          </Sheet>
          <Pop at={at(17, "save")} sfx="confirm">
            <Card style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, padding: "30px 26px" }}>
              <IconBubble size={96} filled>
                <Bookmark size={50} {...icon} />
              </IconBubble>
              <Label size={32}>Save it</Label>
            </Card>
          </Pop>
        </Row>
      </Stage>
    </>
  );
};

const CheckItem: React.FC<{ text: string; at: number }> = ({ text, at: a }) => {
  const p = useIn(a, 10);
  return (
    <Row gap={14} style={{ marginTop: 12 }}>
      <Sfx at={a} type="tick" volume={0.1} />
      <div style={{ width: 38, height: 38, borderRadius: 10, border: `3px solid ${p > 0.5 ? C.blue : C.line}`, background: p > 0.5 ? C.blue : "white", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Check size={26} color="white" {...icon} style={{ opacity: p }} />
      </div>
      <Label size={30} weight={600}>{text}</Label>
    </Row>
  );
};

const SCENES: { lines: number[]; C: React.FC }[] = [
  { lines: [0], C: Hook },
  { lines: [1, 2], C: Design },
  { lines: [3, 4], C: Story },
  { lines: [5, 6], C: Culture },
  { lines: [7], C: Scarcity },
  { lines: [8], C: DropDay },
  { lines: [9, 10], C: Resale },
  { lines: [11, 12], C: Objection1 },
  { lines: [13, 14], C: Objection2 },
  { lines: [15], C: RealProduct },
  { lines: [16, 17], C: Cta },
];

export const DURATION = f(voice.duration);

const Background = () => (
  <AbsoluteFill style={{ background: "white" }}>
    <AbsoluteFill
      style={{
        backgroundImage: `linear-gradient(${C.line} 2px, transparent 2px), linear-gradient(90deg, ${C.line} 2px, transparent 2px)`,
        backgroundSize: "72px 72px",
        backgroundPosition: "-1px -1px",
        opacity: 0.55,
      }}
    />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(255,255,255,0) 45%, rgba(255,255,255,0.95) 100%)" }} />
  </AbsoluteFill>
);

const SceneWrap: React.FC<{ from: number; dur: number; children: React.ReactNode; first: boolean }> = ({ from, dur, children, first }) => {
  const frame = useCurrentFrame();
  const o = first ? 1 : interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const s = interpolate(frame, [0, dur], [1, 1.03]);
  return (
    <SceneFromProvider value={from}>
      <AbsoluteFill style={{ opacity: o, transform: `scale(${s})`, transformOrigin: "50% 45%" }}>{children}</AbsoluteFill>
    </SceneFromProvider>
  );
};

const groups = (() => {
  const out: { start: number; words: { text: string; start: number }[] }[] = [];
  voice.lines.forEach((_, li) => {
    const ws = voice.words.filter((w) => w.line === li);
    const n = Math.ceil(ws.length / 4);
    const size = Math.ceil(ws.length / n);
    for (let i = 0; i < ws.length; i += size) {
      const g = ws.slice(i, i + size).map((w) => ({ text: w.text, start: f(w.start) }));
      out.push({ start: g[0].start, words: g });
    }
  });
  return out;
})();

const Captions = () => {
  const frame = useCurrentFrame();
  let gi = 0;
  for (let i = 0; i < groups.length; i++) if (groups[i].start <= frame) gi = i;
  const g = groups[gi];
  let wi = -1;
  g.words.forEach((w, i) => {
    if (w.start <= frame) wi = i;
  });
  return (
    <div style={{ position: "absolute", top: 1450, left: 90, width: 870, textAlign: "center", fontFamily: SANS, fontWeight: 600, fontSize: 50, color: C.ink, letterSpacing: "-0.01em" }}>
      <span style={{ background: "rgba(255,255,255,0.92)", padding: "8px 20px", borderRadius: 16, boxDecorationBreak: "clone" }}>
        {g.words.map((w, i) => (
          <span key={i} style={{ color: i === wi ? C.blue : C.ink, textDecoration: i === wi ? "underline" : "none", textDecorationThickness: 5, textUnderlineOffset: 10 }}>
            {w.text}
            {i < g.words.length - 1 ? " " : ""}
          </span>
        ))}
      </span>
    </div>
  );
};

export const SafeZone = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {[200, 350, 570, 730, 1300, 1480, 1550].map((y) => (
      <div key={y} style={{ position: "absolute", top: y, left: 0, right: 0, borderTop: "2px dashed red" }} />
    ))}
    <div style={{ position: "absolute", left: 960, top: 0, bottom: 0, borderLeft: "2px dashed red" }} />
  </AbsoluteFill>
);

export const Reel: React.FC<{ guides?: boolean }> = ({ guides }) => {
  const { durationInFrames } = useVideoConfig();
  const starts = SCENES.map((s, i) => (i === 0 ? 0 : lineStart(s.lines[0]) - 12));
  return (
    <AbsoluteFill style={{ fontFamily: SANS }}>
      <Fonts />
      <Background />
      {SCENES.map((s, i) => {
        const from = starts[i];
        const to = i + 1 < SCENES.length ? starts[i + 1] + 12 : durationInFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={to - from}>
            <SceneWrap from={from} dur={to - from} first={i === 0}>
              <s.C />
            </SceneWrap>
          </Sequence>
        );
      })}
      <Captions />
      <Audio src={staticFile("voice.wav")} />
      {guides && <SafeZone />}
    </AbsoluteFill>
  );
};
