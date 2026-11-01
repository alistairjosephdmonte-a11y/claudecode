# BRAND CORONER · CASE 002 · Edit and render report

- Film: 16 scene sequences × 720 frames = 11520 frames = 480.0 s at 24 fps, 1920×1080, 16:9.
- Project: `scenes/BC002_WEWORK.blend`: scenes SC01–SC16 (one orthographic camera each), and BC002_EDIT, whose VSE holds the 16 scene strips back to back (channel 1), the temporary sound design (channel 3), and one narration marker per beat.
- Engine: Workbench, flat lighting, texture colour, 8× AA; view transform Standard (sRGB/Rec.709 transfer), so brand hex values render exactly.
- Delivery encode: H.264 High, yuv420p, CRF 16, BT.709 primaries, transfer and matrix, TV range; AAC 192 kb/s.

## Scenes

| Scene | In | Act | Title | Beats (narration markers) |
|---|---|---|---|---|
| SC01 | 00:00:00 | ACT 01 · the valuation | the $47 billion contradiction | open on the reported 2019 private valuation / the company the number described (archival photography slot) / 2019 valuation versus the november 2023 chapter 11 filing; what went wrong? |
| SC02 | 00:30:00 | ACT 01 · the valuation | the first clue | the bankruptcy filing and its date / how money moved: landlord, wework, member / flexible customers, long-term leases: the contradiction |
| SC03 | 01:00:00 | ACT 02 · the promise | a different kind of office | traditional office versus flexible workspace / what members got (archival photography slots) / the first location, 154 grand street, 2010 |
| SC04 | 01:30:00 | ACT 02 · the promise | selling the future | adam neumann and the expansion narrative (authenticated photo slot) / from one building to 528 locations in 111 cities / growth is not profitability; could the economics support the ambition? |
| SC05 | 02:00:00 | ACT 03 · the machine | the business model | wework leases property from landlords / fits it out and operates it / members pay for access: lease, fit-out, operate, collect revenue |
| SC06 | 02:30:00 | ACT 03 · the machine | the lease mismatch | two commitments of different lengths / the shorter one can end; the longer one remains / what the s-1 disclosed about lease length |
| SC07 | 03:00:00 | ACT 03 · the machine | the expansion machine | the contractual obligations table / $33.95 billion of commenced operating lease payments, undiscounted / plus about $13.1 billion signed but not yet commenced: a separate category |
| SC08 | 03:30:00 | ACT 04 · the documents speak | the ipo document | august 14, 2019: the s-1 is filed / financial statements, risk factors, related-party transactions / the evidence was public |
| SC09 | 04:00:00 | ACT 04 · the documents speak | the financial evidence | 2018 revenue against 2018 net loss / the rows in the filing / revenue was growing; so were the questions |
| SC10 | 04:30:00 | ACT 04 · the documents speak | governance | the 'we' trademark transaction, about $5.9 million / later unwound / high-vote shares: 20 votes, later 10; who controlled the company? |
| SC11 | 05:00:00 | ACT 05 · the break | the failed ipo | august 14, 2019: ipo registration / september 2019: adam neumann steps down as ceo / september 30, 2019: ipo withdrawn; the ipo never happened |
| SC12 | 05:30:00 | ACT 05 · the break | the rescue | softbank's october 2019 financing package / 2021: merger with bowx, public listing / two different measures; the dream was repriced |
| SC13 | 06:00:00 | ACT 06 · the reckoning | a world without offices | 2020: remote work disruption (archival photography slot) / what the company said, and what demand did / restructuring and lease renegotiation; a new shock, an old problem |
| SC14 | 06:30:00 | ACT 06 · the reckoning | the warning | august 2023: the going-concern warning / cash at september 30, 2023: $462 million (unaudited, disclosed november 21) / november 6, 2023: chapter 11; warning and filing are separate events |
| SC15 | 07:00:00 | ACT 06 · the reckoning | what survived | chapter 11 to emergence: november 6, 2023 to june 11, 2024 / the company continued in reorganized form (licensed photography slot) / the business survived; the original valuation story did not |
| SC16 | 07:30:00 | ACT 06 · the reckoning | the final verdict | return to the number / four pieces of evidence / verdict and brand coroner identity |

## Camera smoothness (screen terms, cuts excluded)

Limits: {'pan_fw_s': 0.45, 'pan_acc_fw_s2': 0.6, 'zoom_pct_s': 9.0, 'zoom_acc_pct_s2': 12.0}

| Scene | Cuts | Max pan (frame widths/s) | Max pan acc. | Max zoom (%/s) | Max zoom acc. |
|---|---|---|---|---|---|
| SC01 | 2 | 0.009 | 0.006 | 1.58 | 0.9 |
| SC02 | 1 | 0.091 | 0.058 | 8.91 | 5.15 |
| SC03 | 2 | 0.011 | 0.005 | 2.44 | 1.05 |
| SC04 | 2 | 0.015 | 0.011 | 6.8 | 4.73 |
| SC05 | 0 | 0.0 | 0.0 | 0.57 | 0.16 |
| SC06 | 1 | 0.157 | 0.043 | 4.18 | 2.15 |
| SC07 | 2 | 0.077 | 0.022 | 7.87 | 4.2 |
| SC08 | 5 | 0.07 | 0.018 | 7.7 | 6.92 |
| SC09 | 2 | 0.02 | 0.014 | 7.48 | 5.3 |
| SC10 | 2 | 0.012 | 0.012 | 3.94 | 2.01 |
| SC11 | 1 | 0.389 | 0.334 | 1.69 | 1.4 |
| SC12 | 2 | 0.004 | 0.002 | 0.77 | 0.32 |
| SC13 | 2 | 0.028 | 0.025 | 2.22 | 2.15 |
| SC14 | 2 | 0.044 | 0.026 | 7.15 | 4.2 |
| SC15 | 2 | 0.001 | 0.0 | 1.17 | 0.48 |
| SC16 | 1 | 0.001 | 0.0 | 1.6 | 0.57 |

Flags: none

## Frame check (rendered output)

- frames_expected: 11520
- frames_present: 11520
- missing: []
- wrong_size: []
- unexpected_jumps: []
- unexpected_black_frames: []
- background_mean_8bit: 7.42
- background_target: #080808 = 8
- known_cuts: 45
- per_scene_max_change: {'SC01': 2.63, 'SC02': 9.3, 'SC03': 3.27, 'SC04': 0.65, 'SC05': 0.23, 'SC06': 6.23, 'SC07': 7.84, 'SC08': 23.27, 'SC09': 17.21, 'SC10': 9.06, 'SC11': 4.76, 'SC12': 7.95, 'SC13': 10.21, 'SC14': 7.19, 'SC15': 3.02, 'SC16': 0.58}
- pass: True
