// Central configuration: colours, type, timing. Every scene and sound cue reads from here.
export const VIDEO = { width: 1920, height: 1080, fps: 30, frames: 450 };

export const C = {
  navy: '#101D35', blue: '#0879D9', red: '#E52B2B', gold: '#F5BC35', white: '#F7F5EF',
  ink: '#2b211c', // illustration outline
};

export const FONT = 'Inter';

// Shot boundaries in frames [from, to). Retimed from the brief to fit the real voice durations.
export const SHOTS = {
  arrival: [0, 84], violation: [84, 128], explanation: [128, 190], logic: [190, 272],
  penny: [272, 318], fries: [318, 344], punchline: [344, 420], hold: [420, 450],
} as const;

// Voice clip start frames (durations come from src/generated/voice-durations.json)
export const VOICE = { narrator: 2, sheldon1: 86, leonard1: 130, sheldon2: 192, penny1: 286, sheldon3: 346 } as const;
export const SPEAKER: Record<keyof typeof VOICE, string> = {
  narrator: 'narrator', sheldon1: 'sheldon', leonard1: 'leonard', sheldon2: 'sheldon', penny1: 'penny', sheldon3: 'sheldon',
};

// Caption phrase reveal frames, taken from the speech-to-text word timings of each line
export const CUES = {
  narrA: 37, narrB: 64,
  why: 86, haveYou: 91, movedIt: 99,
  iNeeded: 130, spaceFood: 139,
  seating: 192, follows: 214, geometry: 235,
  comfy: 286, fries: 320,
  thisIs: 346, precisely: 350, whyWe: 365, rules: 389,
  title: 426,
};

// Sound effect cues: [frame, file, volume]
export const SFX: [number, string, number][] = [
  [0, 'door', .55], [4, 'bag', .45], [8, 'step', .35], [20, 'step', .35], [32, 'step', .35], [54, 'step', .3],
  [100, 'fabric', .35], [118, 'creak', .35],
  [132, 'container', .45], [150, 'utensil', .3],
  [196, 'linedraw', .3], [212, 'click', .35], [222, 'click', .35], [244, 'click', .3],
  [272, 'step', .35], [279, 'step', .35], [284, 'sit', .55],
  [319, 'fry_take', .45], [334, 'bite', .5],
  [70, 'click', .15], [392, 'click', .15],
];
export const STING = 424;
export const MUSIC = { base: .42, ducked: .14, rampFrames: 6, endFrame: 417 };
