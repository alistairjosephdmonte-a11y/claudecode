# First-run setup: Clean Cut

Run this the first time the skill is used (the gate in `SKILL.md` sends you here), and again whenever the creator says
"redo my setup". It takes about five minutes. Keep it short: this is a free skill and the creator wants their first
video back, not a long interview.

**Ask one question per message, wait for the answer, save it, then ask the next.** The rules for running the interview
are at the top of `setup/SHARED-SETUP.md`: read them before the first question.

Open with two lines: a few quick questions, asked one at a time, only this once. Then check the tools yourself.

## Part 1: the tools (check, do not ask)

Run section **A6** of `setup/SHARED-SETUP.md`: Node 22 or newer, ffmpeg, and `npx hyperframes doctor`. HyperFrames
renders the captions onto the video. For anything missing, say in one line what it is for, give the one command, and
wait for their yes before installing.

## Part 2: the questions

From `setup/SHARED-SETUP.md`, in this order. Skip anything already in `~/.claude/creator-profile/profile.json`
after reading it back in one line. Save with `python3 setup/apply_profile.py --set key=value`.

1. **A1. Who you are**: name, brand, handle and platform, and the one-sentence niche.
2. **A3. Fonts, the main font only.** "Which font should the captions use?" Find the bold weight on their computer
   exactly as A3 describes and save `font_main_name` and `font_main_bold`. Skip the emphasis and caption-font rows:
   Clean Cut has one plain caption style.
3. **A5. Transcription**: ElevenLabs (recommended) or on this computer (free). Never ask for the key in chat.
4. **A7. Where files live**: only the first row (where finished videos go). Do not ask the others.

Then one question for this skill, saved with `python3 setup/apply_profile.py --set-skill key=value`:

| Ask | Key | Default |
|---|---|---|
| "How do you usually film: camera or phone, horizontal or vertical?" | `camera_setup` | their words |

Do not ask about colours, music, sound effects, B-roll, profile pictures or reference videos. Clean Cut does not use
them. If they bring any of it up, say plainly that it is part of the full Creator Skill Pack (https://editing.ajenepinnock.com/).

## Part 3: finish

1. Read the answers back in three lines. Fix anything they correct.
2. `python3 setup/apply_profile.py`. If it prints `STILL TO ASK` or `UNFILLED`, ask exactly those and run it again.
3. Tell them in two lines that setup is done and that they can drop in a raw talking-head clip and say "clean cut this".
4. Their answers live in one shared profile, so if they get the full pack later it starts from the same answers and
   only asks the new questions.
