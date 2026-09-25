# Higgsfield Creative Workflow: 500 Creatives a Day

A step-by-step playbook for the design team to produce ~500 on-brand ad creatives per day using **Claude Code + the Higgsfield connector**. Claude handles prompt writing, batching, and tracking. Designers handle the brief, the brand lock, and final quality control (QC).

---

## 0. The math

| Item | Number |
|---|---|
| Target shipped creatives / day | **500** |
| Expected QC reject rate | ~25% |
| Generations needed / day | **~650** |
| Max jobs per Higgsfield batch call | 12 |
| Batch calls / day | ~55 |
| Designers | 4 (≈160 generations each, ≈125 shipped each) |

You can't get to 500 by making one creative at a time. The whole workflow turns **one brief into a matrix** of variants and runs that matrix in batches of 12.

**One brief = 1 product × 5 hooks × 5 visual styles × 3 aspect ratios = 75 creatives.**
Around 7 briefs a day, plus re-runs of what fails QC, gets you to 500.

---

## 1. One-time setup (≈30 min per designer)

1. **Install Claude Code** (desktop, web at claude.ai/code, or CLI).
2. **Connect Higgsfield**: claude.ai → Settings → Connectors → Higgsfield → Connect, and sign in to the team's Higgsfield workspace.
3. **Check credits.** 650 generations a day uses a lot of credits. Ask Claude to run a cost preflight on one generation (`generate_image` with `get_cost`) for each model you plan to use, then multiply by 650. Batch calls can't preflight cost.
4. **Clone this repo.** It contains the `/creative-batch` skill (`.claude/skills/creative-batch/SKILL.md`), which runs the whole pipeline below.
5. **Make a shared Drive folder** with this layout:
   ```
   Creatives/
   ├── _brand/            # logos, fonts, palette, approved product shots
   ├── _briefs/           # one brief file per campaign
   └── YYYY-MM-DD/
       ├── <brief-name>/  # generated outputs, grouped by brief
       └── _qc-log.csv    # pass/fail + reason per creative
   ```

---

## 2. Build the brand lock (once per brand, ≈1 hr)

Every prompt reuses this block so that 500 creatives still look like one brand.

- **Reference media:** upload 3–5 approved product shots and the logo to Higgsfield once. Save the media IDs you get back in `_brand/media-ids.txt`. All future generations reference these IDs, so you never re-upload.
- **Style block** (paste into `_brand/style-block.txt`):
  ```
  Palette: #0A2540 navy, #FF6B35 orange accents, white space dominant.
  Lighting: soft daylight, high key. Product always sharp and centered-left.
  Mood: confident, clean, premium. No clutter, no extra logos, no text artifacts.
  ```
- **Do / Don't list:** for example "never show the product on the floor" or "no hands with 6 fingers → reject".

> **Tip:** keep headline text **out** of the generated image. Generate clean visuals, then add copy in Figma/Canva templates. AI text rendering is the #1 cause of QC rejects.

---

## 3. Write the brief (5 min per brief)

Save as `_briefs/<campaign>.md`:

```markdown
Product: Hydra Bottle 750ml
Audience: gym-goers 22–35
Offer: 20% off launch week
Hooks (5):
  1. "Still drinking warm water mid-set?"
  2. Before/after: plastic bottle vs Hydra
  3. Ice still there after 24h
  4. Social proof: "10,000 athletes switched"
  5. Lifestyle: morning run at sunrise
Visual styles (5): studio product, lifestyle UGC, flat-lay, bold graphic, cinematic close-up
Formats (3): 1:1 feed, 4:5 feed, 9:16 stories/reels
Video?: yes, 10 of the 75 as 5s motion versions (9:16)
```

---

## 4. Generate: the daily pipeline

Open Claude Code in this repo and run:

```
/creative-batch _briefs/hydra-bottle.md
```

Claude then:

1. **Expands the matrix:** 5 hooks × 5 styles × 3 ratios = 75 prompts. Each one combines hook + style + brand style block + brand reference media IDs. You'll see the prompt table before anything is spent.
2. **Picks the model:** uses Higgsfield `models_explore` (recommend) to choose the best image model for the style, or uses the one the team has standardised on.
3. **Submits in batches of 12** (`generate_image_batch`). 75 prompts = 7 batches.
4. **Waits** on each batch (`jobs_wait`, groups of ≤12) and records every job ID with its matrix index, so nothing gets lost or double-charged if something times out.
5. **Shows results** in one gallery (`show_generation_by_ids`, up to 60 per view).
6. **Makes video variants:** takes the best 10 approved stills and animates them (`generate_video_batch`, `9:16`, image as reference media).

### Suggested daily schedule (per designer)

| Time | Block | Output |
|---|---|---|
| 09:30–10:00 | Write/refresh 2 briefs | 2 briefs |
| 10:00–11:00 | Run brief #1 → QC | ~60 shipped |
| 11:00–12:00 | Run brief #2 → QC | ~60 shipped |
| 13:00–14:00 | Re-run rejects + video variants | ~15–20 shipped |
| 14:00–16:00 | Add copy in templates, export, upload | final files |
| 16:00–16:30 | Log winners/losers, update prompts | learning loop |

4 designers × ~125 = **500/day**.

---

## 5. QC: the 30-second checklist

Reject if **any** of these fail, and log the reason in `_qc-log.csv`:

- [ ] Product shape, color, and label match the reference
- [ ] No distorted hands, faces, or extra limbs
- [ ] No garbled text or fake logos in the image
- [ ] Palette and mood match the brand lock
- [ ] Composition leaves room for the headline in the template
- [ ] Nothing offensive, misleading, or off-claim

Then ask Claude: *"re-run rejects from the QC log with the fixes"*. It rewrites only the failed prompts, based on the logged reasons.

---

## 6. Finishing and export

1. Drop approved visuals into **Figma/Canva templates** (one per aspect ratio) with headline, offer, CTA, and logo.
2. **Accessibility check** before export:
   - Text contrast ≥ **4.5:1** (≥ 3:1 for large headlines)
   - Minimum ~24px text on 1080px canvases
   - Write **alt text** for each creative. Ask Claude to draft it from the prompt.
   - Video: burned-in captions if there's voiceover. No flashing more than 3 times/sec.
3. Name files `brand_campaign_hook-style_ratio_v1.png` so performance data maps back to the matrix.

---

## 7. Learning loop (weekly)

- Pull ad performance by hook and style (from the filename).
- Drop the bottom 2 hooks and bottom 2 styles; add new ones.
- Move winning prompts into `_brand/winning-prompts.md`. Claude reuses them as seeds.
- Track reject rate per model. If a model goes above 30%, switch it.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Product looks different each time | Always pass the brand reference media IDs; describe the product identically every time |
| Batch timed out | Don't resubmit the whole batch. Ask Claude to check the saved job IDs first, then retry only the missing ones |
| Credits burning too fast | Draft on a cheaper model, then re-render only QC winners on the premium model |
| Everything looks the same | Styles in the brief are too similar. Make each one a distinct lighting + setting + camera combo |
| Asked "unlimited vs credits?" | Higgsfield asks this when a free allowance covers the model. Answer once and it's remembered for a few minutes |
