import React from 'react';
import { registerRoot, Composition, staticFile, delayRender, continueRender } from 'remotion';
import { Main } from './Main';
import { FPS, DURATION } from './config';

const fontHandle = delayRender('Loading fonts');
Promise.all([
  new FontFace('Anton', `url(${staticFile('fonts/Anton-400.woff2')})`),
  new FontFace('Inter', `url(${staticFile('fonts/Inter-600.woff2')})`, { weight: '600' }),
  new FontFace('Inter', `url(${staticFile('fonts/Inter-500.woff2')})`, { weight: '500' }),
].map((ff) => ff.load().then((l) => document.fonts.add(l)))).then(() => continueRender(fontHandle));

const Root = () => (
  <Composition id="SeatIsTaken" component={Main} durationInFrames={DURATION} fps={FPS} width={1920} height={1080} />
);
registerRoot(Root);
