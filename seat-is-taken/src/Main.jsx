import React from 'react';
import { AbsoluteFill, Sequence, Audio, staticFile, interpolate } from 'remotion';
import { C, SHOTS, VO, SFX, FPS } from './config';
import { Arrival, Violation, Explanation, Logic, PennyArrives, Fries, Reaction, Hold } from './scenes/Scenes';

const SCENES = [['arrival', Arrival], ['violation', Violation], ['explanation', Explanation], ['logic', Logic], ['penny', PennyArrives], ['fries', Fries], ['reaction', Reaction], ['hold', Hold]];

// Music sits under everything, ducks beneath dialogue, dips for the punchline and finishes cleanly.
const speaking = (f) => Object.values(VO).some(({ from, dur }) => f >= from - 3 && f <= from + dur * FPS + 4);
const musicVolume = (f) => {
  const base = speaking(f) ? 0.16 : 0.5;
  const drop = interpolate(f, [338, 344, 398, 404], [1, 0.35, 0.35, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const end = interpolate(f, [432, 449], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return base * drop * end;
};

export const Main = () => (
  <AbsoluteFill style={{ background: C.mustard }}>
    {SCENES.map(([k, Comp]) => (
      <Sequence key={k} name={k} from={SHOTS[k][0]} durationInFrames={SHOTS[k][1] - SHOTS[k][0]}>
        <Comp />
      </Sequence>
    ))}
    <Audio src={staticFile('audio/music.wav')} volume={musicVolume} />
    {Object.entries(VO).map(([k, { from }]) => (
      <Sequence key={k} name={`vo-${k}`} from={from}><Audio src={staticFile(`audio/${k}.wav`)} volume={1} /></Sequence>
    ))}
    {SFX.map(([file, from, vol], i) => (
      <Sequence key={i} name={`sfx-${file}`} from={from}><Audio src={staticFile(`audio/${file}.wav`)} volume={vol} /></Sequence>
    ))}
  </AbsoluteFill>
);
