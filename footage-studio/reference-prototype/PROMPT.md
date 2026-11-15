# Paste this into Claude Code or Codex

You are taking over a product called Footage Studio - a local desktop app
that AI-tags video footage for production houses and wedding studios and
builds a searchable clip library. This folder is a self-contained handover:
everything you need is in it.

First read HANDOVER.md in full. It has two halves: a REFERENCE PROTOTYPE
(working, demo-tested Python source you can mine or rebuild) and a
FRESH-BUILD BRIEF (the product requirements, stated independently - where
the two disagree, the brief wins). Do not trust assumptions that conflict
with HANDOVER.md.

Key rules while you work:
- Keep the trust model intact: non-destructive by default, explicit consent
  before any frames leave the machine, the API key is session-only and never
  persisted, no cost numbers in user-facing text.
- Real AI tagging has never run against the live Anthropic API - treat that
  code path as unproven until a real run passes.
- In the prototype, re-running reuses cached tags; only `sort --rescan`
  (CLI) or deleting _Library/catalog.json forces re-tagging.

Task: begin a fresh build against the FRESH-BUILD BRIEF in HANDOVER.md,
reusing the reference prototype where it genuinely helps. Mac is the first
target platform. Work in small verified steps, keep the acceptance checks
in HANDOVER.md passing, and tell me what you changed and why.
