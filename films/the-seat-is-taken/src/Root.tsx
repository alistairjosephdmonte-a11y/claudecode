import { Composition } from 'remotion';
import { SeatIsTaken } from './SeatIsTaken';
import { VIDEO } from './config';

export const RemotionRoot = () => (
  <Composition id="SeatIsTaken" component={SeatIsTaken} durationInFrames={VIDEO.frames} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
);
