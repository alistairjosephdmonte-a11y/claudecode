import { Config } from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setConcurrency(4);
Config.setPixelFormat('yuv420p');
// Use the system's headless Chrome when one is provided (e.g. Playwright's); otherwise Remotion downloads its own.
if (process.env.REMOTION_CHROME) Config.setBrowserExecutable(process.env.REMOTION_CHROME);
