# QC report: Brand Coroner · Case 002 · WeWork, "the $47 billion illusion" (final production)

## Technical checks

| Check | Result |
|---|---|
| Runtime | **10:06 (606.2 s), 14,548 frames at 24 fps.** The approved narration (1,186 words) at a natural documentary pace of 134 wpm needs 8:50 of speech alone, so the 8:00 target was not forced; the narration was not sped up, as the brief instructs |
| 4K master | 3840×2160, H.264, Rec.709 SDR (bt709 primaries, transfer and matrix), stereo 48 kHz AAC |
| 1080p YouTube | 1920×1080 downscale of the 4K master, H.264, Rec.709, stereo 48 kHz |
| Picture | Rendered in four chunks of 3,637 frames, each verified, then concatenated. No gaps or duplicated frames |
| Sound | The approved narration, verbatim (109 lines; Chatterbox voice, the same Brand Coroner narrator timbre as Case 001), over the original underscore and Foley. Music ducks about 9 dB under the voice. −16 LUFS integrated |
| Narration check | Every line was transcribed by Whisper and compared with the script. The only differences were number formatting ("$47 billion") and "we work" spacing. Two lines were re-voiced ("risk" heard as "wrist"; "questioned" heard as "question") and now match |
| Subtitles | `BRAND_CORONER_CASE002_WEWORK_EN.srt`: 146 cues, at most 2 rows × 42 characters, timed from word timestamps |
| Sync | Each scene's design is time-warped onto the voiceover, so key beats land on their lines (e.g. the $47B figure on "forty-seven billion dollars", the timeline stopping on "formally withdrew", the cards converging on "the combination of…"). Timeline markers sit at every line start in the .blend |
| Project | `wework.blend` (Blender 4.2 LTS): 16 scene meta strips S01–S16, 613 editable strips, 109 line markers, relative asset paths. `vo/timeline.json` holds scene lengths and warps |
| Review | 540p review master rendered first; 96 frames checked (one every 5 s). Fixed: the scene 04 S-1 quote card was too small to read. Single-frame white "cut-in" flashes are intentional |

## Storyboard and fact-check alignment

- **Scene 01:** "2023: chapter 11" label.
- **Scene 02:** red line for long-term lease commitments; off-white line for flexible membership revenue.
- **Scene 03:** three-panel layout: space / services / flexibility. The 2018 photos are labelled as not from the first years.
- **Scene 04:** genuine S-1 statements on community and growth. The music dips at "growth ≠ profitability". Only the verified first location is plotted, plus the cities shown in the photos.
- **Scene 06:** "illustrative comparison · not to scale". The S-1 terms are quoted on a card; no contract lengths are invented.
- **Scene 08:** a red line connects the three evidence windows.
- **Scene 09:** $1.61B is labelled as the net loss attributable to WeWork Companies Inc., with the $1.93B total net loss alongside. All bars share one scale.
- **Scene 11:** ✕ marks the withdrawal; the line breaks.
- **Scene 12:** three components, not a single sum (WeWork release, Oct 22, 2019). Merger closed Oct 20, 2021 (8-K). Different measures; no percentage decline computed.
- **Scene 13:** dated evidence: the 10-K fiscal 2022 COVID-19 statement and the 10-Q (Q2 2023) churn statement. No invented statistics.
- **Scene 14:** day-scaled timeline: Aug 8 warning → Sep 30 quarter end → Nov 6 Chapter 11 → Nov 21 disclosure of $462M (unaudited).
- **Scene 15:** 218 days. Emergence from the 8-K: "The Plan became effective on June 11, 2024".
- **Scene 16:** each card cites evidence shown earlier. Identity: "brand coroner" with a red period; "every brand leaves evidence."

## Notes for review

1. **Runtime 10:06, not 8:00.** See above. To land at 8:00 the script would need to drop to about 950 words, or be read noticeably faster.
2. **Two narration lines differ slightly from the filings.** They are voiced verbatim; the screen carries the precise label.
   - Scene 09, "a net loss of approximately one point six billion": $1.61B is the net loss attributable to WeWork Companies Inc.; the total net loss was $1.93B.
   - Scene 14: the $462M (Sep 30, 2023) is spoken before "On November sixth… filed", but it was disclosed on Nov 21, 2023. The day-scaled timeline shows the true order.
3. **Scene 13 narration** ("negotiated lease changes, exited locations") has no matching on-screen numbers. None were invented; the dated 10-K and 10-Q statements are shown.
4. **Genuine SEC page images** need a declared SEC contact. Filings are flat transcriptions labelled "not a facsimile"; the bankruptcy petition is the real court document. The 8-K Oct 26, 2021 and 8-K Jun 12, 2024 quotes come from your fact-check file.
5. **Photography gaps:** there is no licensable early-era (2010–2014) or post-2024 WeWork photography, so dated 2018 photos are used. The pandemic offices (Vienna, IAEA 2020) are labelled as general context.
6. **Brand typeface:** Outfit (OFL) stands in until the Brand Coroner font file is supplied.
