import React, { useState } from 'react';
import { AbsoluteFill, useCurrentFrame, staticFile, continueRender, delayRender } from 'remotion';
import { SHOTS, FONT } from './config';
import { Soundtrack } from './audio/Soundtrack';
import { Shot01Arrival } from './scenes/Shot01Arrival';
import { Shot02Violation } from './scenes/Shot02Violation';
import { Shot03Explanation } from './scenes/Shot03Explanation';
import { Shot04Logic } from './scenes/Shot04Logic';
import { Shot05Penny } from './scenes/Shot05Penny';
import { Shot06Fries } from './scenes/Shot06Fries';
import { Shot07Punchline } from './scenes/Shot07Punchline';
import { Shot08Hold } from './scenes/Shot08Hold';

const ORDER: [keyof typeof SHOTS, React.FC<{ f: number }>][] = [
  ['arrival', Shot01Arrival], ['violation', Shot02Violation], ['explanation', Shot03Explanation], ['logic', Shot04Logic],
  ['penny', Shot05Penny], ['fries', Shot06Fries], ['punchline', Shot07Punchline], ['hold', Shot08Hold],
];

// load the local font before any frame renders
const useFont = () => {
  const [handle] = useState(() => delayRender('font'));
  useState(() => {
    const ff = new FontFace(FONT, `url(${staticFile('fonts/Inter.ttf')})`, { weight: '100 900' });
    ff.load().then(f => { (document.fonts as any).add(f); continueRender(handle); }).catch(e => { console.error(e); continueRender(handle); });
    return null;
  });
};

export const SeatIsTaken: React.FC = () => {
  useFont();
  const f = useCurrentFrame();
  const shot = ORDER.find(([k]) => f >= SHOTS[k][0] && f < SHOTS[k][1]) ?? ORDER[ORDER.length - 1];
  const Shot = shot[1];
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', fontFamily: FONT }}>
      <Shot f={f} />
      <Soundtrack />
    </AbsoluteFill>
  );
};
