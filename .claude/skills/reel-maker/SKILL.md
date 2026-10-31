---
name: reel-maker
description: Make clean, narrated Instagram Reels (9:16) entirely in code with Remotion — hook, scenes, voiceover, word-synced captions and sound — in a calm "notebook" style that explains things simply. Use when the user asks to make, script, design or render a Reel, Short or TikTok, or to recreate a reference reel's structure in their own style.
---

# Reel Maker

You make short vertical videos as code. Every frame is a React component rendered by Remotion, so there are no AI video credits and the style is fully controllable.

The goal of every reel: **one idea, explained so simply a beginner gets it on first watch.** Clear beats clarity, every time.

## 0. Setup (first run only)

1. Create a Remotion project if none exists: `npx create-video@latest` (blank template). Say yes to the Agent Skills, or run `npx skills add remotion-dev/skills`.
2. Install helpers: `npm i lucide-react @remotion/google-fonts @remotion/media`.
3. Voiceover (free, local): Kokoro TTS.
   - Mac: `brew install espeak-ng ffmpeg`
   - `python3 -m venv .venv && .venv/bin/pip install kokoro soundfile`
   - Male voices: `am_michael`, `am_adam`, `bm_george`. Female: `af_heart`, `af_bella`.
4. Ask the user for: the topic or reference reel, the comment keyword for the giveaway, and male or female voice.

## 1. Script (do this before any visuals)

Write 10–30 short lines, one sentence or phrase each. Each line becomes one beat on screen.

Structure that works:
1. **Hook (line 1):** a bold, specific claim. "This Claude skill makes unlimited reels."
2. **Stakes / twist (lines 2–3):** why it matters, or what's surprising.
3. **"Let me show you how it works."**
4. **The steps or the mechanism**, one idea per line.
5. **Objections, voiced by the viewer:** "You might be thinking…" Then answer each one.
6. **Proof:** real examples or real numbers only. Never invent stats.
7. **CTA:** "Comment KEYWORD and I'll send you ___." Then "Save this so you can come back to it."

Rules: short words, no jargon without a picture, no line longer than about 12 words. Read it aloud; cut anything that doesn't move the story.

## 2. Voice and timing

- Generate the voiceover with word timestamps (Kokoro returns token start/end times). Save `voice.wav` plus `voice.json` with `{lines:[{text,start,end}], words:[{line,text,start,end}]}`.
- Aim for 0.2–0.3s gaps between lines. Speed 1.2–1.35 suits Reels pacing.
- Spell tricky names phonetically for the TTS ("F F mpeg", "Y T D L P"), then map them back to the real spelling in captions.
- **Everything syncs to the voice:** scene start = line start − 12 frames (the scenes crossfade), and every pop, check or highlight fires on the exact spoken word.

## 3. Look ("notebook" style)

- **Background:** white with a faint 72px grid and a soft white vignette.
- **Colors:** ink `#141414`, one accent blue `#3B62DB`, soft blue `#EAF0FD`, muted `#8A8A8A`, lines `#E6E6E6`. One accent only.
- **Type:** Manrope (600–800) for text; Instrument Serif *italic* in the accent color for the key phrase of every headline. Tight letter-spacing (−0.035em) on big text.
- **Headline pattern:** one bold sans line, then one blue italic serif line. "Start on / *your desktop.*"
- **Illustrations:** Lucide icons, one 3px outline weight everywhere, rounded cards with a soft shadow, paper sheets with a folded corner, flat blue folders. No stock art, no gradients, no neon.
- **Mascot (optional):** a simple line-art character in the corner whose mouth moves while the voice speaks. It goes big and centered for punchline beats. Never use a real person's face without permission.

## 4. Layout and the Instagram safe zone (1080×1920)

| Zone | Position |
|---|---|
| Section header / kicker | y ≈ 205–300 |
| Headline | y ≈ 350–570 |
| Main visual (stage) | y ≈ 730–1300 |
| Mascot (small) | bottom right, about x 810–950, y 1280–1420 |
| Captions | y ≈ 1480 |
| Keep clear | above y=200 (top bar), below y≈1550 (caption and audio text), right of x=960 (like/comment buttons) |

Check every scene by rendering stills with these lines drawn on top before rendering the full video.

## 5. Scene rules (what keeps it easy to follow)

1. **The topic is always on screen.** Every scene has a headline that says what is happening.
2. **No empty frames.** A scene arrives with its main visual already showing. Spoken keywords only *change* things inside it (a check appears, a word gets struck through, a card slides in).
3. **Show literally what is said.** "Three folders" means three folders appear one by one, as each name is spoken.
4. **One idea per scene.** If you need a second idea, make a second scene.
5. **Calm motion:** expo-out easing `cubic-bezier(0.16,1,0.3,1)`, 12-frame crossfades, a slow 3% drift. No shakes, glitches or flashing.
6. **Something always moves:** typing, a progress bar, a filling checklist, a drawing line.
7. **Captions:** 3–4 words at a time, Manrope 600 at 50px, with the spoken word in the accent color and underlined.

## 6. Sound

- Voice at full level. Small UI sounds (pop, tick, confirm, key) at 8–16% volume on the exact frames things appear. Free CC0 packs: Kenney "Interface Sounds".
- Leave music out of the render. The user adds a trending track in the Instagram app (licensed) at low volume.

## 7. Render and export

- 1080×1920, 30fps, H.264, CRF 16–18.
- Normalize audio: `ffmpeg -i raw.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -movflags +faststart reel.mp4`
- Remind the user to turn on Instagram's **AI label** when the voice is AI-generated.

## 8. Deliver with the reel

- A caption: a hook line, 3–5 short bullet lines, the comment keyword CTA, a save prompt, and at most 5 hashtags.
- The giveaway the CTA promises (a guide, prompts, a template). It must exist before posting.

## Final checklist

- [ ] Hook on screen in the first second
- [ ] Every line has a visual that literally shows it
- [ ] No frame with only a title and captions
- [ ] Everything inside the safe zone
- [ ] Captions synced word by word
- [ ] Real claims only; no invented numbers
- [ ] Audio at about −14 LUFS
- [ ] Caption and giveaway ready
