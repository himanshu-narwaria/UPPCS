# Master prompt: build the three UPPSC files for a new subject folder

Use this to turn one Ghatna Chakra Preview PDF into the same three files every finished subject has
(full notes, quick notes, 72-hour plan), wired into the study dashboard and the website.

## How to use

1. Start a new Claude Code session in the `Indian History` project folder.
2. Copy the prompt below (everything inside the box) into the chat.
3. Replace the six `{…}` values with one row from the table at the end. Do one subject per session.

---

```text
Build the three UPPSC study files for one new subject, in the same format as the finished
subjects, and wire them into the dashboard and website.

SUBJECT     = {SUBJECT}          e.g. Indian History
HINDI       = {HINDI}            e.g. भारतीय इतिहास
FOLDER      = {FOLDER}           folder inside this project that holds the PDF
PDF         = {PDF}              file name of the PDF in that folder
PREFIX      = {PREFIX}           short lowercase file prefix, e.g. history
PROGRESS_KEY= {KEY}              localStorage key for the 72h plan, e.g. his72-done (must be unique)

## Who it is for
A UPPSC aspirant (UP PCS and related UPPSC exams), not UPSC. UPPCS Prelims is on 6 December 2026.
The paper is bilingual, so add standard Hindi terms in brackets at first use.

## Style (my standing preferences)
Plain white background. Readable fonts: Atkinson Hyperlegible Next for body, Lexend for headings,
embedded as data: URIs so everything works offline (copy the @font-face blocks from an existing
file). Very simple English, point-wise and minimal, no repetition. Facts asked in two or more
UPPSC papers are highlighted separately from facts asked once.

## Read first, in this order
1. The memory notes for this project (they describe earlier decisions).
2. The finished Polity files, which are the templates to copy:
   - Indian_Polity_2026/polity-uppsc-full-notes.html   (full notes)
   - Indian_Polity_2026/polity-in-72h.html             (72-hour plan)
   - Environment_2025/environment-2025-uppsc-quick-notes.html (quick notes)
   Reuse their CSS, JavaScript, class names and ids. Change only the content.
3. dashboard-src/build_dashboard.py, sitenav.py and security.py: they parse these files, so the
   HTML must keep the hooks listed under "File contract".
4. The whole PDF {FOLDER}/{PDF}. Read every page before deciding the structure.

## Outputs (all inside {FOLDER}/)
1. {PREFIX}-uppsc-full-notes.html : every chapter in short points, tagged by UPPSC papers;
   "Most repeated", "Latest UPPSC" and a "UPPSC PYQ practice" mode with every UPPSC MCQ.
2. {PREFIX}-uppsc-quick-notes.html: the same chapters, much shorter, revision-only; must use
   exactly the same chapter numbers and titles as the full notes.
3. {PREFIX}-in-72h.html: 72 one-hour sessions before 6 December 2026, each with its reading and
   that hour's UPPSC PYQs, tick-off progress, and four timed mocks at the end.
Keep every build script you write in dashboard-src/subjects/{PREFIX}/ (never in a temp folder),
so all three files can be rebuilt from the PDF text by running one command.

## Method
- Extract the PDF text page by page. Two-column pages, tables, maps and flowcharts often come out
  scrambled: render those pages to images and read them visually.
- Check that the book's index page numbers match where each chapter really starts (in the Polity
  book the index ran about three pages ahead). Build the chapter list from the real headings.
- Make a page ledger: every page → chapter → content type. Nothing may be skipped.
- Parse every question: stem, options, exam label(s), keyed answer, explanation, page.

## Content rules
- Completeness first: every name, date, number, list item and table row survives. Compress
  wording, never coverage.
- Never turn a wrong option or a false statement into a fact. Read the key and explanation first.
- Keep qualifiers (only, first, not, except, largest) and the book's time context.
- Where the book's key looks wrong or conflicts, keep it and mark the line "Check".
- Anything not from the book (updates, 2025 papers) is labelled as such, with its source.

## PYQ rules
- Count UPPSC papers only (PCS Pre and Mains, RO/ARO, Lower Subordinate, UDA/LDA, GIC, BEO, RI).
  Other states' and UPSC questions may support facts but never enter UPPSC counts.
- A repeat is the same fact asked in a different paper. The same question printed twice counts once.
- Add UPPSC papers newer than the book only if you can verify them, labelled with their key status
  (official or provisional). Never present a coaching answer as official.
- All counts are computed by script from the tagged questions, never typed by hand.

## File contract (the dashboard and website parse these exact hooks)
Full notes and quick notes:
- <header class="top"> containing <button id="menu" …>, then <main>.
- <section class="view" id="home"> with a contents list where each chapter is exactly
  <a href="#cN"><span class="no">N</span><span class="nm">Title</span><span class="q">K UPPSC PYQs</span></a>
  (an optional <span class="p up">Most asked</span> may sit before the "q" span).
- Chapter views <section class="view ch" id="cN" data-title="Title">, topics
  <article class="topic" id="cN-tK">, and <nav class="pn"> previous/next links.
- <section class="view" id="repeated">.
Full notes only:
- <script id="pqd" type="application/json"> with every UPPSC MCQ as
  {"ch":"cN","y":YEAR,"e":"PCS Pre ’10","s":stem,"o":[options],"k":[answer indexes],"f":feedback,"n":papers,"h":"cN-tK"}.
  Each chapter's K in the contents must equal its number of questions here.
- The repeated view says "N facts asked in two or more UPPSC papers" and each row is
  <summary><span class="t">fact</span><span class="ps"><span class="p up">×N</span></span></summary><div class="yrs"><div>papers</div><a href="#cN-tK">…
- A <section class="view" id="latest"> and a <p class="foot"> source line on the home view.
Quick notes only:
- In the repeated view: <h3 id="rep-facts" class="sec">N facts asked in two or more UPPSC papers</h3><ol class="rows">…</ol>
  with one <summary> per fact.
- Home view <p class="foot">Based on N UPPSC questions (…) …</p>, where N equals the chapter totals.
72-hour plan:
- The exact phrase "72 hours before 6 December 2026" on the home view.
- Progress saved with localStorage.getItem("{KEY}") / setItem("{KEY}", …).
- <nav class="side" id="side"> with phase labels <div class="lb">Learn</div>, <div class="lb">Revise</div>,
  <div class="lb">Test</div> (add "UP and current" between Learn and Revise if the subject has UP facts),
  and hours 1–72 in order as <a href="#hN" data-v="hN"><span>N</span>Title</a>.
- Learn-hour titles use the full-notes chapter titles exactly: "Title", "Title · part k of n",
  "Title A + Title B", or "Title A to Title C".
- Hour views <section class="view" id="hN" data-n="N"> ending in a .done block with a
  "Mark hour N done" button and an <a class="btn nx" href="#hN+1"> link.
All three:
- No outside scripts, images, fonts or iframes; no onclick= style attributes; no javascript: links;
  no forms. (The site's Content-Security-Policy blocks them.)
- Every external source link uses target="_blank" rel="noopener noreferrer".

## Process
- Use at most 2 helper agents at medium effort, splitting the chapters between them, then one
  critic pass at the end by a fresh agent that checks numbers and facts against the PDF.
- Run a coverage check per chapter: compare every page's names and numbers with the notes and
  explain every miss.

## Wire it in
1. Add the subject to SUBJECTS in dashboard-src/build_dashboard.py:
   {"key": "{PREFIX}", "name": "{SUBJECT}", "hindi": "{HINDI}", "folder": "{FOLDER}"},
2. Run: python dashboard-src/build_dashboard.py
   It must finish with no errors and no "sitenav warning" lines. It rebuilds the dashboard, adds
   the menu, breadcrumbs and related links to the new pages, and regenerates vercel.json.

## Verify before delivering
- Open all three files in Chrome: no console errors, nothing scrolls sideways at 360 px,
  search works, practice answers, progress ticks persist, the Subjects menu opens.
- Every link resolves. The dashboard shows the new subject with all three files.
- Spot-check at least 20 facts and every count shown on the dashboard against the PDF.

## Deliver
Commit as himanshu-narwaria (this repository's git config is already set; Vercel blocks other
authors) and push to origin main. PDFs stay out of git. Then tell me in plain words what was
built, the counts, what you could not verify, and anything I should check.
```

---

## Values for the subjects waiting in this project

| SUBJECT | HINDI | FOLDER | PDF | PREFIX | KEY |
|---|---|---|---|---|---|
| Indian History | भारतीय इतिहास | Indian_History_Part_2 | Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf | history | his72-done |
| General Geography | सामान्य भूगोल | General_Geography_Part_3 | Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf | geography | geo72-done |
| General Science | सामान्य विज्ञान | General_Science_Part_7 | Preview_General_Science_Part_7_2026_26121_C_E_Book_combined_1.pdf | science | sci72-done |

These books are large (History and Science 760 pages each, Geography 708), so expect each subject
to take a long session.

`Indian_Polity_and_Governance` holds a copy of the same Polity PDF that `Indian_Polity_2026`
already covers, so it needs no new files.
