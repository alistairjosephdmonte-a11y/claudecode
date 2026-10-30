# QC report: Trimming Through the Ages (4:3 master)

## Measured

| Check | Spec | Result |
|---|---|---|
| Duration | 300 s | 300.000 s ✅ |
| Frames | 7200 @ 24 fps | 7200 ✅ |
| Resolution | 1440×1080 (4:3) | 1440×1080 ✅ |
| Chapters | 10 × 30 s (720 frames each) | each chapter verified at 720 frames before concat ✅ |
| Loudness | −14 LUFS integrated | −14.2 LUFS, LRA 6.8 LU ✅ |
| Narration | every line inside its beat, never sped up | all 50 lines fit (see narration-script.md); ASR-checked ✅ |
| Voice vs bed | voice clearly above music/Foley | ≥ 7.8 dB ✅ |
| Wash | exactly one, sap green, final reveal only | only in ch. 10 beat 5 ✅ |
| Outlines | never black | ink is #2d3263 navy ✅ |
| Copy | handwritten, no boxes | Patrick Hand with soft paper halo knock-out ✅ |
| Motion | drawings 12 fps, camera/wash 24 fps, no dissolves | ✅ (page turns only between chapters) |
| Music | small instruments only | ukulele, nylon guitar, bassoon, clarinet, toy piano, recorder, woodblock, music box, glockenspiel ✅ |

Spot-check frames: `qc/contact.jpg` (one per chapter plus the end card), `qc/frames/`.

Delivered file: `trimming-through-the-ages-4x3.mp4` is a 94 MB two-pass H.264 encode (2.35 Mb/s) of the CRF-20 master, to fit the repository limit; the full-quality master renders from `source/build.sh`.

## Open items (need a decision or client input)

1. **Brand assets not supplied.** The packshot and wordmark slots in ch. 10 show labelled dashed crayon placeholders. Drop the approved `packshot.png` and `wordmark.png` into `assets/brand/` and re-render chapter 10 only (see `assets/brand/README.md`). Nothing brand-related is drawn or lettered by hand.
2. **The white-wax slogan is faintly visible before the wash.** This is physically honest (real wax resist catches the light) but it slightly pre-empts the reveal. It can be made fully invisible if preferred.
3. **Supporting characters added beyond the brief:** butler, squire, blacksmith, senate clerk, mission controller, and two background philosophers. They are generic, invented and modest.
4. **Copy halo.** Where the copy sits over busy floors, the paper is cleared softly around the letters. Please confirm that this reads as "printed on the page" and not as a subtitle.
5. **16:9 and 9:16 versions** are not made yet; they will follow after approval of this master.

## Compliance notes
- All incidents are invented comedy. No real people are depicted or quoted.
- The brand's origin is not placed in any historical era; the brand appears only in the modern-age chapter.
