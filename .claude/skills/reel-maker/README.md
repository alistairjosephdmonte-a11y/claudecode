# Reel Maker: a Claude skill

Make clean, narrated Instagram Reels entirely in code. No video editor, no AI video credits.

## Install (2 minutes)

**Claude Code (desktop app or terminal)**
1. Unzip this folder.
2. Put the `reel-maker-skill` folder inside your project at `.claude/skills/` (create the folder if it doesn't exist). To use it in every project, put it in `~/.claude/skills/` instead.
3. Open Claude Code in that project and ask:
   > Use the reel-maker skill to make a reel about [your topic]. Comment keyword: [WORD]. Male voice.

**Claude.ai (web or app)**
Settings → Capabilities → Skills → Upload skill → choose this zipped folder.

## What it does

- Writes a short, hook-first script for you (claim → how it works → objections → proof → CTA)
- Generates a free voiceover with Kokoro and syncs everything to the words
- Builds every scene in Remotion in a clean "notebook" style
- Keeps everything inside Instagram's 9:16 safe zone
- Exports an upload-ready MP4, plus a caption and a giveaway checklist

## Needs

- Claude Code (paid Claude plan) or Claude.ai with skills enabled
- Node.js, plus Python 3 for the voiceover
- Remotion is free for individuals and teams of up to 3 people (remotion.dev/license)

Made with ❤️ and code. Follow for more AI builds.
