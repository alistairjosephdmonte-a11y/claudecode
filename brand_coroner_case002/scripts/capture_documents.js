// Renders exact crops of the filed SEC documents (the filed HTML, rendered by Chromium, unedited) and records the pixel
// rectangles of the phrases the film highlights. Nothing is retyped: every crop is a screenshot of the original filing.
//   node scripts/capture_documents.js
// Output: evidence/document_crops/<id>.png + metadata/document_crops.json
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "evidence", "sec_filings");
const OUT = path.join(ROOT, "evidence", "document_crops");

// anchor: phrase that locates the crop. block: ancestor used for the crop ("table" or "p"). above/below: extra px.
// marks: phrases whose rectangles are recorded for the red highlight (searched inside the crop only).
const CROPS = [
  { id: "D01_S1_COVER", file: "S1_20190814.htm", anchor: "As filed with the Securities and Exchange Commission on August", block: "p", above: 10, below: 330, marks: ["August 14, 2019", "The We Company"] },
  { id: "D02_8K_CH11", file: "8K_20231107_ch11.htm", anchor: "(the “Petition Date”)", block: "p", above: 70, below: 10, marks: ["On November 6, 2023", "Chapter 11"] },
  { id: "D03_LEASE_TABLE", file: "S1_20190814.htm", anchor: "Non-cancelable operating lease commitments", block: "table", above: 10, below: 10, nth: 0, marks: ["33,953,402", "Non-cancelable operating lease"] },
  { id: "D04_LEASE_FOOTNOTE", file: "S1_20190814.htm", anchor: "Excludes an additional $13.1 billion", block: "table", above: 30, below: 30, marks: ["$13.1 billion", "not yet commenced"] },
  { id: "D05_SELECTED_FINANCIALS", file: "S1_20190814.htm", anchor: "Net loss attributable to WeWork Companies Inc.", block: "table", above: 0, below: 0, nth: 0, marks: ["1,821,751", "(1,610,792)", "Net loss attributable to WeWork Companies Inc.", "(1,927,419)"] },
  { id: "D06_TRADEMARK", file: "S1_20190814.htm", anchor: "with a fair market value of approximately $5.9 million", block: "p", above: 160, below: 60, marks: ["approximately $5.9 million", "in lieu of paying cash"] },
  { id: "D07_TRADEMARK_UNWOUND", file: "S1A_20190904.htm", anchor: "Unwinding of Receipt of Partnership Interests", block: "p", above: 10, below: 170, marks: ["Unwinding of Receipt of Partnership Interests"] },
  { id: "D08_TWENTY_VOTES", file: "S1_20190814.htm", anchor: "have twenty votes per share", block: "p", above: 60, below: 40, marks: ["twenty votes per share", "one vote per share"] },
  { id: "D09_TEN_VOTES", file: "S1A_20190913.htm", anchor: "decrease from 20 votes per share to 10 votes per share", block: "p", window: true, above: 120, below: 90, marks: ["from 20 votes per share to 10 votes per share"] },
  { id: "D10_RISK_FACTORS", file: "S1_20190814.htm", anchor: "future undiscounted minimum lease cost payment obligations under signed operating and finance leases was", block: "p", above: 40, below: 40, marks: ["$47.2 billion", "approximately 15 years"] },
  { id: "D11_RW_WITHDRAWAL", file: "RW_20190930.htm", anchor: "hereby requests that the Commission consent to the withdrawal", block: "p", above: 470, below: 40, marks: ["consent to the withdrawal of the Registration Statement", "September 30, 2019"] },
  { id: "D12_SOFTBANK_RELEASE", file: "SB_20191023.htm", anchor: "This includes $5 billion in new", block: "p", window: true, above: 150, below: 78, marks: ["$5 billion in new", "up to $3 billion", "$1.5 billion"] },
  { id: "D13_BOWX_EV", file: "BOWX_ex991.htm", anchor: "initial enterprise value of approximately $9 billion", block: "p", above: 60, below: 60, marks: ["initial enterprise value of approximately $9 billion"] },
  { id: "D14_SPAC_CLOSE", file: "8K_20211026_close.htm", anchor: "As a result of and upon the Closing, which occurred on October 20, 2021", block: "p", above: 10, below: 10, marks: ["October 20, 2021"] },
  { id: "D15_GOING_CONCERN", file: "10Q_20230808.htm", anchor: "substantial doubt exists about the Company", block: "p", window: true, above: 150, below: 40, marks: ["substantial doubt exists about the Company’s ability to continue as a going concern", "higher member churn and weaker demand"] },
  { id: "D16_Q3_CASH", file: "EX991_2023Q3.htm", anchor: "As of September 30, 2023, the Company had $462 million", block: "p", above: 10, below: 100, marks: ["$462 million", "September 30, 2023"] },
  { id: "D17_EMERGENCE", file: "8K_20240612_emerge.htm", anchor: "The Plan became effective on June 11, 2024", block: "p", above: 10, below: 10, marks: ["The Plan became effective on June 11, 2024"] },
  { id: "D18_FIRST_LOCATION", file: "S1_20190814.htm", anchor: "In early 2010, we opened our doors to our first member community at 154 Grand Street", block: "p", above: 10, below: 10, marks: ["154 Grand Street in New York City", "528", "111 cities across 29 countries"] },
  { id: "D19_COVID_10K", file: "10K_2022.htm", anchor: "COVID-19", block: "p", above: 10, below: 10, nth: 2, marks: ["COVID-19"] },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 1200 }, deviceScaleFactor: 2 });
  const meta = {};
  let loaded = null;
  for (const c of CROPS) {
    if (loaded !== c.file) {
      await page.goto("file://" + path.join(SRC, c.file), { waitUntil: "load", timeout: 120000 });
      await page.addStyleTag({ content: "html,body{background:#fff !important}" });
      loaded = c.file;
    }
    const r = await page.evaluate((c) => {
      const norm = (s) => s.replace(/[ \s]+/g, " ");
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      // locate the anchor across text nodes inside block elements
      const blocks = [...document.querySelectorAll(c.block === "table" ? "table" : "p, div, td, li")];
      const hits = blocks.filter((b) => norm(b.textContent).includes(norm(c.anchor)) && (c.block === "table" || ![...b.children].some((k) => norm(k.textContent).includes(norm(c.anchor)) && /^(P|DIV|TD|LI)$/.test(k.tagName))));
      const el = hits[c.nth || 0];
      if (!el) return null;
      let br = el.getBoundingClientRect();
      const sx = window.scrollX, sy = window.scrollY;
      if (c.window) {
        // crop a fixed window around the anchor phrase itself (for documents whose blocks are very tall)
        const w2 = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n2;
        while ((n2 = w2.nextNode())) {
          const t = n2.textContent.replace(/\u00a0/g, " "); const i = t.indexOf(c.anchor);
          if (i >= 0) { const rg = document.createRange(); rg.setStart(n2, i); rg.setEnd(n2, i + c.anchor.length); const q = rg.getBoundingClientRect(); br = { left: br.left, width: Math.min(br.width, 1000), top: q.top, height: q.height }; break; }
        }
      }
      let clip = { x: Math.max(0, br.left + sx - 24), y: Math.max(0, br.top + sy - c.above), w: Math.min(document.documentElement.scrollWidth, br.width + 48), h: br.height + c.above + c.below };
      if (clip.w < 760) { const cx = clip.x + clip.w / 2; clip.w = 760; clip.x = Math.max(0, cx - 380); }
      const marks = [];
      for (const m of c.marks) {
        // find text node ranges matching m (single-node match, normalized whitespace)
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n, found = false;
        while ((n = walker.nextNode()) && !found) {
          const t = n.textContent.replace(/ /g, " ");
          let i = t.indexOf(m);
          while (i >= 0) {
            const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + m.length);
            const rects = [...rg.getClientRects()].map((q) => ({ x: q.left + sx, y: q.top + sy, w: q.width, h: q.height }));
            if (rects.length && rects.every((q) => q.y >= clip.y && q.y + q.h <= clip.y + clip.h)) {
              marks.push({ text: m, rects: rects.map((q) => ({ x: q.x - clip.x, y: q.y - clip.y, w: q.w, h: q.h })) });
              found = true; break;
            }
            i = t.indexOf(m, i + 1);
          }
        }
        if (!found) marks.push({ text: m, rects: [] });
      }
      return { clip, marks };
    }, c);
    if (!r) { console.log("MISSING", c.id); meta[c.id] = { file: c.file, missing: true }; continue; }
    const png = path.join(OUT, c.id + ".png");
    await page.screenshot({ path: png, clip: { x: r.clip.x, y: r.clip.y, width: r.clip.w, height: r.clip.h }, fullPage: true });
    meta[c.id] = { file: c.file, png: path.relative(ROOT, png), css_w: r.clip.w, css_h: r.clip.h, scale: 2, marks: r.marks };
    console.log(c.id, Math.round(r.clip.w), Math.round(r.clip.h), r.marks.map((m) => m.text.slice(0, 18) + ":" + m.rects.length).join(" "));
  }
  fs.writeFileSync(path.join(ROOT, "metadata", "document_crops.json"), JSON.stringify(meta, null, 2));
  await browser.close();
})();
