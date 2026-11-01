import { Composition } from "remotion";
import { DURATION, Reel } from "./Reel";

export const RemotionRoot = () => (
  <>
    <Composition id="SneakerReel" component={Reel} durationInFrames={DURATION} fps={30} width={1080} height={1920} defaultProps={{ guides: false }} />
    <Composition id="SneakerReelGuides" component={Reel} durationInFrames={DURATION} fps={30} width={1080} height={1920} defaultProps={{ guides: true }} />
  </>
);
