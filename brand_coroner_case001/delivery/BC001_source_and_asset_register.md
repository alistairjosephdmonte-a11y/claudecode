# BRAND CORONER · CASE 001 · Source and asset register

A figure renders as final only when its source status is verified_primary or verified_secondary; otherwise graphics carry a PENDING tag.

## Sources

| ID | Status | Citation | Used for | Note |
|---|---|---|---|---|
| SRC_RANDOLPH_2019 | verified_publication | Marc Randolph, That Will Never Work (Little, Brown, 2019) | Randolph's recollection of the September 2000 Dallas meeting, the $50 million figure and the reaction he describes. | One participant's memoir. Recollection, not a transcript. |
| SRC_INC_2019_EXCERPT | verified_secondary | [Inc., excerpt of That Will Never Work (2019), archived copy](https://gwern.net/docs/www/www.inc.com/9f8939c6b25070c4677db37b5c9ebda5787814aa.html) | Confirms the excerpt places the meeting at Blockbuster headquarters in Dallas. | Secondary reproduction of the memoir. |
| SRC_ANTIOCO_DISPUTE | pending_primary_source | Accounts attributed to John Antioco disputing details of the meeting | The film's second account. Only secondary, biography-style summaries were found during research. | BLOCKER for final graphics: obtain a primary interview or statement before rendering S06 as final. |
| SRC_BBI_10K_FY2004 | verified_primary | [Blockbuster Inc., Form 10-K for fiscal 2004 (SEC EDGAR)](https://www.sec.gov/Archives/edgar/data/1085734/000119312505063510/d10k.htm) | Late fees ('extended viewing fees') ended January 1, 2005 at more than 4,500 company-operated U.S. stores. | Also the expected location of the year-end 2004 store count (see SRC_STORES_2004). |
| SRC_BBI_10K_FY2005 | verified_primary | [Blockbuster Inc., Form 10-K for fiscal 2005 (SEC EDGAR)](https://www.sec.gov/Archives/edgar/data/0001085734/000119312506055023/d10k.htm) | Eliminated fees were about 14% of 2004 rental revenues; about $60 million in initial marketing and implementation costs in Q1-Q2 2005; rental revenues fell 5.0% from 2004. | Primary source for S15, S28, S29. |
| SRC_STORES_2004 | pending_primary_check | Approximately 9,100 stores worldwide at year-end 2004 (brief figure) | S13 store count. | Not found in research. Confirm in the FY2004 10-K (Item 1/Item 2) before rendering final. |
| SRC_EVF_2004 | pending_primary_check | Approximately $622.4 million extended viewing fee revenue in 2004 (brief figure) | S15 dollar value. | Not found in research. The FY2004 10-K projected $400-450 million for 2005 instead. Confirm before final. |
| SRC_RENTAL_REDUCTION_2005 | pending_primary_check | More than $500 million reduction in 2005 rental revenue (brief figure) | S29. | Not supported by research: the FY2005 10-K reports rental revenues down 5.0%. Reconcile before final; never present as profit loss. |
| SRC_BB_ONLINE_2004 | pending_primary_check | Blockbuster Online launch, August 2004 (brief figure) | S25 launch date. | Launch year 2004 widely reported; the month was not confirmed. |
| SRC_TOTAL_ACCESS_2006 | verified_secondary | [Blockbuster Total Access launched November 1, 2006 (press coverage)](https://archives-new.honoluluadvertiser.com/article/2006/Nov/02/bz/FP611020318.html) | S30-S31: launch date and in-store returns of mailed discs. | Import the original Blockbuster press release for final. |
| SRC_TA_SUBSCRIBERS | pending_primary_check | Total Access subscriber counts (storyboard: 2.2M 2006, 3M+ Apr 2007) | S32 bars. | Research found 'more than 2 million' reported in early 2007 (Hollywood Reporter). Exact values unconfirmed. |
| SRC_NFLX_INSTANT_2007 | verified_primary | [Netflix press release, January 16, 2007: instant viewing on PCs](https://about.netflix.com/en/news/netflix-offers-subscribers-the-option-of-instantly-watching-movies-on-their) | S35: announced January 2007, initially about 1,000 titles, Windows PCs. |  |
| SRC_BBI_CH11_2010 | verified_secondary | [Blockbuster Chapter 11 filing, September 23, 2010 (Bloomberg; TechCrunch)](https://www.bloomberg.com/news/2010-09-23/blockbuster-video-rental-chain-files-for-bankruptcy-protection.html) | S41 filing date; stores and online service continued operating during the case (S42). | Import the court petition or Form 8-K scan for the document graphic; none is rendered until imported. |
| SRC_SCALE_2000 | pending_primary_check | Relative size of Blockbuster and Netflix in 2000 | S23 qualitative comparison. | Use FY2000 filings (revenue, stores, subscribers) before showing any numbers. Shown only as not-to-scale blocks. |
| SRC_NFLX_NO_LATE_FEES | pending_primary_check | Netflix subscription without late fees (circa 1999-2000) | S19 narration line. | Widely reported; import a primary Netflix source. |

## Assets

status 'pending' = must be replaced/approved before final; nothing pending is presented as authentic

| ID | Type | Status | Location | Note |
|---|---|---|---|---|
| AST_FONT_INTER | font | verified_license | assets/fonts_reference_only/Inter-*.otf | SIL OFL 1.1 (license copied) |
| AST_LOC_BOARDROOM | environment | internal_generated | scenes/BC001_LOC_BOARDROOM.blend | Representative, not a specific room |
| AST_LOC_STORE | environment | internal_generated | scenes/BC001_LOC_STORE.blend | Representative store, full/reduced inventory variants |
| AST_LOC_WAREHOUSE | environment | internal_generated | scenes/BC001_LOC_WAREHOUSE.blend | Representative fulfilment facility |
| AST_LOC_ARCHIVE | environment | internal_generated | scenes/BC001_LOC_ARCHIVE.blend | Investigative light table |
| AST_DALLAS_MASSING | environment | internal_generated | scenes/BC001_MASTER.blend#SET_ENV_01_DALLAS | Stylised massing; no identifiable buildings |
| AST_DALLAS_OBS_TOWER_PROXY | reference_geometry | pending | DAL_ObservationTower_Proxy_REF_PENDING | Replace with verified reference geometry |
| AST_BRAND_BLOCKBUSTER_SIGNAGE | brand | pending | ST_Fascia_Panel_Blank | Blank panel until an approved brand reference is supplied |
| AST_BRAND_NETFLIX_MAILER | brand | pending | PROP_S17/S18 envelopes | Plain editorial red; no logo until approved reference |
| AST_BRAND_TOTAL_ACCESS_MAILER | brand | pending | PROP_S31_Mailer_EditorialBlue | Plain editorial blue |
| AST_LIKENESS_RANDOLPH | likeness | pending | S05/S08/S46 source cards | Authenticated photo required; slot labelled |
| AST_LIKENESS_ANTIOCO | likeness | pending | S06/S08/S46 source cards | Authenticated photo required; slot labelled |
| AST_DOC_10K_FY2005 | document_scan | pending | assets/documents/ | Import verified SEC scan for S28 (placeholder bars only) |
| AST_DOC_CH11_PETITION | document_scan | pending | assets/documents/ | Import court petition or 8-K for S41 |
| AST_AUDIO_NARRATION | audio | pending | audio/narration/ | Record from BC001_narration_script.md; SRT holds timing |
| AST_AUDIO_SCORE | audio | pending | audio/music/ | Original score to be composed and cleared |
| AST_AUDIO_SFX | audio | pending | audio/sfx/ | Licensed or recorded effects per audio_cue_manifest.json |
