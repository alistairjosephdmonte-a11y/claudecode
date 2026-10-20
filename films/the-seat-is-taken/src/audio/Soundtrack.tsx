// Audio sequencing: voices at their cue frames, sound effects from config, the music bed with
// automatic ducking under every voice line, room tone, and the final sting.
import React from 'react';
import { Audio, Sequence, staticFile, interpolate } from 'remotion';
import { VOICE, SFX, STING, MUSIC, VIDEO } from '../config';
import durs from '../generated/voice-durations.json';

const voiceSpans = (Object.keys(VOICE) as (keyof typeof VOICE)[]).map(k => [VOICE[k], VOICE[k] + Math.ceil((durs as Record<string, number>)[k] * VIDEO.fps)]);
export const musicVolume = (f: number) => {
  let duck = 0;
  for (const [a, b] of voiceSpans) duck = Math.max(duck, interpolate(f, [a - MUSIC.rampFrames, a, b, b + MUSIC.rampFrames], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
  return MUSIC.base + (MUSIC.ducked - MUSIC.base) * duck;
};

export const Soundtrack: React.FC = () => (
  <>
    <Audio src={staticFile('audio/sfx/roomtone.wav')} volume={.5} />
    <Audio src={staticFile('audio/music.wav')} volume={musicVolume} />
    {(Object.keys(VOICE) as (keyof typeof VOICE)[]).map(k => (
      <Sequence key={k} from={VOICE[k]} layout="none"><Audio src={staticFile(`audio/voice/${k}.wav`)} volume={1} /></Sequence>
    ))}
    {SFX.map(([f, name, v], i) => (
      <Sequence key={i} from={f} layout="none"><Audio src={staticFile(`audio/sfx/${name}.wav`)} volume={v} /></Sequence>
    ))}
    <Sequence from={STING} layout="none"><Audio src={staticFile('audio/sting.wav')} volume={.6} /></Sequence>
  </>
);
