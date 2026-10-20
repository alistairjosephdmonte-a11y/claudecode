// Centralized palette, layout and timing. All timing in frames at 30 fps.
export const FPS = 30;
export const DURATION = 450; // exactly 15 s

export const C = {
  mustard: '#FFB33F',
  charcoal: '#262626',
  red: '#D62D2D',
  blue: '#0879D9',
  teal: '#168D70',
  white: '#F7F5EF',
  gold: '#F2A900',
  couch: '#8C4B2C',
  couchDark: '#6F3A22',
  couchLight: '#A35C38',
  skin: '#EBC09C',
};

export const FONT = { head: 'Anton, sans-serif', body: 'Inter, sans-serif' };

// Shared stage geometry so the couch, cushion and seating positions stay identical across shots.
export const STAGE = { floor: 860, seatY: 650, couchX: 800, couchW: 1000 };
export const SEATS = { left: -300, mid: 0, right: 250 }; // x offsets from couch centre

// Shot windows [from, to). Re-timed from the storyboard to fit the measured dialogue durations.
export const SHOTS = {
  arrival: [0, 93],
  violation: [93, 131],
  explanation: [131, 180],
  logic: [180, 270],
  penny: [270, 306],
  fries: [306, 340],
  reaction: [340, 405],
  hold: [405, 450],
};

// Voice clips: start frame and measured duration (s) from scripts/vo.py.
export const VO = {
  narrator: { from: 3, dur: 2.995 },
  sheldon1: { from: 96, dur: 1.055 },
  leonard1: { from: 134, dur: 1.595 },
  sheldon2: { from: 186, dur: 2.624 },
  penny1: { from: 279, dur: 0.902 },
  sheldon3: { from: 341, dur: 2.104 },
};

// Sound-effect cues: [file, frame, volume].
export const SFX = [
  ['door', 0, 0.7], ['bag', 22, 0.55], ['bag', 52, 0.35], ['click', 36, 0.4], ['click', 72, 0.5],
  ['cushion', 93, 0.7], ['creak', 99, 0.35], ['click', 104, 0.45],
  ['container', 140, 0.6], ['utensil', 150, 0.5], ['click', 152, 0.4],
  ['marker', 190, 0.5], ['marker', 204, 0.45], ['marker', 218, 0.45], ['click', 232, 0.4], ['click', 246, 0.45], ['marker', 250, 0.4],
  ['creak', 283, 0.65],
  ['container', 311, 0.45], ['pickup', 318, 0.6], ['bite', 330, 0.55], ['click', 314, 0.4],
  ['click', 343, 0.35], ['click', 365, 0.35], ['sting_small', 404, 0.75],
  ['sting_final', 418, 0.55], ['creak', 412, 0.25],
];

export const lerp = (a, b, k) => a + (b - a) * k;
