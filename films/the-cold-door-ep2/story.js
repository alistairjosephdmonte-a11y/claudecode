// The Cold Door, episode 2: "Why don't casinos have clocks?" Same grammar as episode 1 (see ../milk-toon/story.js).
// Sources, in order of use: Las Vegas Advisor (2009) on where casino clocks are; casino.org "Vegas Myths Busted" (Bill Friedman's 2021 and 2024 remarks;
// Wynn & Roger Thomas from 1980); Mental Floss on Friedman's 2000 book; University of Guelph (Karen Finlay) on playground vs. gaming design;
// Noseworthy & Finlay (2009), Journal of Gambling Studies, 160 slot players; NZ Ministry of Health venue study (2007–2010, published 2012);
// Natasha Dow Schüll, Addiction by Design (2012); McGill Office for Science and Society + Gambling.com test on the oxygen myth.
export const CAST = { H: { name: 'HAL', voice: 'am_onyx', speed: .9, col: '#E07A2E' }, D: { name: 'DOT', voice: 'af_jessica', speed: 1.06, col: '#C8326B' } };
export const TITLE = ['WHERE DID ALL', 'THE CLOCKS GO?'];
export const END = { ep: '> EPISODE 2: WHY DON\'T CASINOS HAVE CLOCKS?', line: 'Removing a clock is easy. Removing time takes design.' };
export const TARGET = 300;
export const SEQ = [
  ['W', 'home', 'STOCKROOM · 2:14 AM', { cold: 1 }],
  ['S', 'ins:card'], ['A', 2.4, 'cardIn'],
  ['L', 'D', 'c01', "New card. Why don't casinos have clocks. Hal, that's the one everybody knows. They hide the clocks so you lose track of time.", { shot: 'cuD' }],
  ['L', 'H', 'c02', 'Everybody knows it.', { shot: 'cuH', pause: .6 }],
  ['L', 'H', 'c03', "That's usually when I get the basket.", { shot: 'two', act: 'openPortal', pause: .6 }],
  ['L', 'D', 'c04', 'No. No, I am not going to Las Vegas in an apron.', { shot: 'cuD', act: 'panic' }],
  ['A', 3.0, 'title', { shot: 'title' }],

  // ── the dark Strip, 1950s to the 80s ──
  ['W', 'strip', 'LAS VEGAS · THE DARK YEARS, 1950s–80s'],
  ['L', 'D', 'c05', "Oh, it's so dark. Where are the windows? Where's the outside?", { shot: 'wide' }],
  ['L', 'H', 'c06', 'From the fifties to the eighties, a lot of Strip casinos really did look like this. No windows. No clocks on the floor.', { shot: 'two' }],
  ['L', 'D', 'c07', 'So it is a trick! Case closed.', { shot: 'cuD', act: 'hope' }],
  ['L', 'H', 'c08', 'Ask the man who wrote the book on it.', { shot: 'cuH', pause: .4 }],

  ['W', 'maze', 'THE BOOK · CASINO DESIGN, 2000'],
  ['L', 'H', 'c09', 'Bill Friedman ran two Las Vegas casinos, and wrote a six hundred page book on how to lay one out. Thirteen principles. Low ceilings. A maze of short, winding paths.', { shot: 'two', act: 'friedman' }],
  ['L', 'D', 'c10', "I'm in a maze again. Why am I always in a maze.", { shot: 'cuD', act: 'panic' }],
  ['L', 'H', 'c11', 'But on clocks, Friedman says the time trick is a myth. He says it was the serious gamblers who demanded the clocks and windows go. Or they would not come back.', { shot: 'cuH' }],
  ['L', 'D', 'c12', 'The gamblers asked for it?', { shot: 'cuD', act: 'blank', pause: .4 }],
  ['L', 'H', 'c13', 'In his words, they "don\'t want time." They came for a fantasy. An escape.', { shot: 'two', pause: .8 }],

  // ── where the clocks actually are ──
  ['W', 'book', 'CLOCK HUNT · THE SPORTS BOOK'],
  ['L', 'D', 'c14', 'Wait. Wait! A clock! There is a clock right there!', { shot: 'wide', act: 'clocks' }],
  ['L', 'H', 'c15', "The race and sports book. Bets close minutes before the race starts, so here a clock earns its keep. You'll often find one on the cashier's cage, and on the pit podiums by the tables too.", { shot: 'two' }],
  ['L', 'D', 'c16', 'So the clocks are where the staff need them.', { shot: 'cuD' }],
  ['L', 'H', 'c17', 'And almost never above the slot machines.', { shot: 'cuH', pause: .4 }],
  ['W', 'tower', 'ATLANTIC CITY · 2000'],
  ['A', 1.6, 'tower', { shot: 'wide' }],
  ['L', 'D', 'c18', 'Hal, that clock is the size of a house.', { shot: 'cuD', act: 'blank' }],
  ['L', 'H', 'c19', 'In two thousand, Bally\'s in Atlantic City put a thirty-four foot clock tower in a slot parlour. A Vegas columnist called it the only main floor casino clock he knew of.', { shot: 'two', pause: .5 }],

  // ── the playground ──
  ['W', 'garden', 'THE PLAYGROUND · FROM 1980'],
  ['L', 'D', 'c20', 'Oh. Flowers. Daylight. High ceilings. This is nice. Why is this nice?', { shot: 'wide', act: 'hope' }],
  ['L', 'H', 'c21', 'From nineteen eighty, Steve Wynn and his designer Roger Thomas went the other way. Light, art, open space. The playground style. Think Mirage, think Bellagio.', { shot: 'two' }],
  ['L', 'H', 'c22', 'Researchers at the University of Guelph stopped forty-eight people leaving Las Vegas casinos. They rated the playground ones higher for pleasure, and for feeling restored.', { shot: 'cuH' }],
  ['L', 'D', 'c23', 'So the nice casino is the honest one.', { shot: 'cuD', act: 'hope', pause: .4 }],
  ['L', 'H', 'c24', 'The lead researcher, Karen Finlay, said people in a playground casino stay longer, feel better, and bet more. They lose more. And they come back.', { shot: 'cuH', pause: .9, act: 'cold' }],
  ['L', 'D', 'c25', 'The nice one is worse.', { shot: 'cuD', act: 'deflate', pause: .4 }],

  // ── the lab: sound bends time ──
  ['W', 'lab', 'THE LAB · 160 SLOT PLAYERS'],
  ['L', 'H', 'c26', 'In two thousand and nine, Noseworthy and Finlay sat one hundred and sixty people at slot machines, then asked how long they had played.', { shot: 'two', act: 'lab' }],
  ['L', 'H', 'c27', 'With ordinary casino noise, the bells and the chatter, people underestimated the time. Add music, and they guessed better. Best of all with slow, loud music.', { shot: 'ins:lab' }],
  ['L', 'D', 'c28', 'So the noise eats the clock.', { shot: 'cuD' }],
  ['L', 'H', 'c29', 'The noise eats the clock.', { shot: 'cuH', pause: .5 }],
  ['W', 'venue', 'NEW ZEALAND · CLOCKS ON THE WALL'],
  ['L', 'H', 'c30', 'And clocks on the wall may not save you. A New Zealand government study of gambling venues found about one in three gamblers underestimated how long they had stayed. Even with clocks on the machines, and in the room.', { shot: 'two', act: 'clocks' }],
  ['L', 'D', 'c31', 'The clock was right there!', { shot: 'cuD', act: 'panic' }],
  ['L', 'H', 'c32', 'And the more time they lost, the longer they played.', { shot: 'cuH', pause: .6 }],

  // ── the zone ──
  ['W', 'zone', 'THE MACHINE ZONE'],
  ['A', 2.2, 'zone', { shot: 'ins:zone' }],
  ['L', 'H', 'c33', 'The anthropologist Natasha Dow Schüll spent years with machine gamblers in Las Vegas. Her book is called Addiction by Design.', { shot: 'two' }],
  ['L', 'H', 'c34', 'Many players described a trance they called the zone. Worries fade. Even the body fades. They are not playing to win. They are playing to keep playing.', { shot: 'cuH' }],
  ['L', 'D', 'c35', 'Curd. Curd! Get away from the slot machine!', { shot: 'cuD', act: 'scream' }],
  ['A', 1.6, 'curdSlot', { shot: 'ins:curdslot' }],
  ['L', 'H', 'c36', 'The industry has a name for what it measures. Time on device.', { shot: 'cuH', pause: 1.2, act: 'cold' }],

  // ── myth check ──
  ['W', 'air', 'MYTH CHECK · THE AIR'],
  ['L', 'D', 'c37', 'Okay, but they pump in extra oxygen to keep you awake, right? Everyone knows that.', { shot: 'two' }],
  ['L', 'H', 'c38', 'Everybody knows it.', { shot: 'cuH', pause: .3 }],
  ['L', 'H', 'c39', "A test on the Strip found twenty point nine percent oxygen. Same as outside. Scientists at McGill point out extra oxygen would just be a fire hazard. The story seems to come from a novel.", { shot: 'ins:meter' }],
  ['L', 'D', 'c40', 'I hate that I believed that.', { shot: 'cuD', act: 'deflate', pause: .4 }],

  // ── the suspiciously normal world ──
  ['W', 'beige', 'PRESENT DAY · A VERY NORMAL CASINO'],
  ['A', 2.0, 'normal', { shot: 'wide' }],
  ['L', 'D', 'c41', 'Why is this one so beige.', { shot: 'two' }],
  ['L', 'H', 'c42', 'Because today it barely matters. Everyone carries a clock in their pocket. Most casinos don\'t bother hiding the time any more.', { shot: 'two', act: 'phones' }],
  ['L', 'D', 'c43', 'So it was never really about the clock.', { shot: 'cuD', pause: .5 }],
  ['L', 'H', 'c44', 'Removing a clock is easy. Removing time takes the room, the sound, and the machine.', { shot: 'cuH', pause: .8 }],

  // ── home ──
  ['W', 'home', 'STOCKROOM · ???'],
  ['L', 'D', 'c45', "Okay. Dear customer. Casinos rarely put clocks on the gaming floor. Gamblers asked for that. But the real time thief is the noise, the comfort, and the zone.", { shot: 'two', act: 'write' }],
  ['L', 'H', 'c46', 'Good.', { shot: 'cuH', pause: .5 }],
  ['L', 'D', 'c47', 'Hal. What time is it?', { shot: 'cuD', pause: 2.4, act: 'cold' }],
  ['L', 'H', 'c48', 'I took the clocks out of the stockroom years ago.', { shot: 'cuH', pause: .5 }],
  ['L', 'D', 'c49', 'Why?', { shot: 'cuD', act: 'twitch', pause: .4 }],
  ['L', 'H', 'c50', 'The serious stockers asked.', { shot: 'cuH', pause: 1.0 }],
  ['A', 6.5, 'end', { shot: 'end' }],
];
