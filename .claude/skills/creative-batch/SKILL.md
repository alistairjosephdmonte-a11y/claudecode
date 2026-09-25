---
name: creative-batch
description: Turn a creative brief into a hook × style × aspect-ratio matrix and mass-generate ad creatives with the Higgsfield connector in batches of 12. Use when a designer runs /creative-batch <brief-file>, or asks to "run the brief", "generate the creative matrix", "re-run QC rejects", or "make video variants" for the high-volume creative workflow in docs/higgsfield-creative-workflow.md.
---

# Creative Batch

Full team playbook: `docs/higgsfield-creative-workflow.md`.

## Inputs
- A brief file (argument), with product, hooks, visual styles, formats, and whether video is wanted.
- Brand lock files if present: `_brand/style-block.txt`, `_brand/media-ids.txt`, `_brand/winning-prompts.md`.
  If they're missing, ask the designer for the style block and reference media IDs before generating.

## Steps

1. **Expand the matrix.** Make one prompt per hook × style × aspect ratio. Each prompt:
   - describes the product identically every time (copy the brief's wording)
   - describes the hook as a visual scene, **with no rendered text or headlines** (copy goes on in templates later)
   - appends the brand style block verbatim
   - gets a stable `index` (0..N-1) and a slug `hook-style_ratio`
2. **Show the prompt table** (index, slug, ratio, first ~80 chars of the prompt) and the total count. Wait for the designer's go-ahead before spending credits.
3. **Pick the model.** Use the team's standard model if the designer names one. Otherwise call Higgsfield `models_explore` with `action: "recommend"` for the style. Check each model's `medias[].roles` so reference images get the right role.
4. **Submit** with `generate_image_batch`, at most 12 requests per call. Each request gets `count: 1`, `aspect_ratio`, `prompt`, and `medias` from `_brand/media-ids.txt`.
   If the response returns `unlim_choice`, ask the designer once and resend with `use_unlim` set.
5. **Record every job ID** against its index and slug straight away, in a table in the chat and in `<date>/<brief>/jobs.csv` if the designer is working in a local folder. Never resubmit a batch blindly after a timeout or partial failure. Check the recorded job IDs first and retry only the items that have no job.
6. **Wait** with `jobs_wait` in groups of ≤12. When `all_terminal` is false, poll again after `poll_after_seconds`.
7. **Display** all terminal jobs with one `show_generation_by_ids` call per 60 jobs. Summarise successes and failures by index and slug.
8. **Video variants** (if the brief asks): after the designer picks winners, animate them with `generate_video_batch` (`aspect_ratio: "9:16"`, the winning image's job_id as reference media, short duration). Then follow steps 5–7 again.

## Re-running QC rejects
Read `_qc-log.csv` (slug, pass/fail, reason). For each fail, change only what the reason names (e.g. "garbled text" → add "no text, no lettering"; "wrong product color" → restate the color and re-attach the reference). Then resubmit only those items with their original indices.

## Finishing help
On request, draft alt text for approved creatives (one sentence: subject, action, setting, no "image of"). Also remind designers of the contrast rule (≥4.5:1 body text, ≥3:1 large text) before export.
