// Story timeline: the single source of truth (seconds). Narration durations: voices/dur.json
export const DUR = 123.5;
export const OPEN = [3.5, 6.0];
export const TURNS = [[24.0, 26.6], [54.4, 57.0], [68.6, 71.2], [87.2, 89.8]];
export const CLOSE = [110.6, 113.4];

// [id, start, displayed text]
export const VO = [
  ['p1', 7.0, "Long ago, by the river Tamasa, the sage Valmiki saw a hunter's arrow strike one of two krauncha birds."],
  ['p2', 15.2, "His grief poured out as a verse — the first poem, it is said — and in that rhythm he sang the story of Rama, in seven books."],
  ['s1a', 27.6, "Prince Rama of Ayodhya won Princess Sita by breaking the mighty bow of Shiva."],
  ['s1b', 34.0, "But on the eve of his crowning, Queen Kaikeyi claimed two old promises: her son Bharata would rule, and Rama would live fourteen years in the forest."],
  ['s1c', 44.8, "Rama went without anger, with Sita and his brother Lakshmana. Bharata ruled only in his name, with Rama's sandals on the throne."],
  ['s2a', 58.4, "In the forest, Ravana, the ten-headed king of Lanka, lured Rama away with a golden deer — and carried Sita off through the sky."],
  ['s3a', 72.4, "Searching for her, Rama found allies: the monkey king Sugriva, and wise, mighty Hanuman."],
  ['s3b', 79.4, "Hanuman leapt across the ocean, found Sita in a grove of ashoka trees, and gave her Rama's ring."],
  ['s4a', 91.0, "An army of monkeys built a bridge of stones to Lanka. Rama defeated Ravana, and came home to be crowned."],
  ['s4b', 98.8, "In the last book, which many scholars believe was added later, Sita found refuge with Valmiki, where her twin sons learned his poem, and sang it before Rama himself."],
  ['end', 113.8, "Grief by a river became a poem. And people have been singing it ever since."],
];

// hanging signs: [t0, t1, ribbon, title, gloss]
export const CHAPTERS = [
  [26.4, 30.4, 'Books 1 & 2', 'Bala · Ayodhya', 'childhood · exile'],
  [57.0, 61.0, 'Book 3', 'Aranya', 'the forest'],
  [71.0, 75.0, 'Books 4 & 5', 'Kishkindha · Sundara', 'allies · the leap'],
  [89.8, 93.8, 'Books 6 & 7', 'Yuddha · Uttara', 'war · the last book'],
];
// the first verse (Bala Kanda 1.2.15), on a scroll
export const SHLOKA = { t0: 16.2, t1: 23.8,
  lines: ['मा निषाद प्रतिष्ठां त्वमगमः शाश्वतीः समाः ।', 'यत्क्रौञ्चमिथुनादेकमवधीः काममोहितम् ॥'],
  gloss: '“Hunter, may you find no rest for endless years, for you killed one of a loving pair.”' };
export const ACTIONS = [[31.2, 'SNAP!', ['#fff35a', '#ff9a2e']], [80.6, 'LEAP!', ['#a8f0ff', '#3fa1ff']]];
export const TITLE = { t0: 115.6 };
export const CREDITS = [
  'Narration: Kokoro TTS · Music & sound: synthesized · Room, desk & props: Poly Haven (CC0)',
  'A retelling after Valmiki’s Ramayana, the Sanskrit epic in seven books',
];
