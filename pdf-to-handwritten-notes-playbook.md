# Playbook: turn any study PDF into handwritten-style HTML revision notes

Use this the next time you have a topic PDF. It is the same method used for the *UPPSC Prelims 2025 Quick Revision* notes, written so that **nothing in the PDF gets left out**.

---

## 0. How to use this file

Attach these three things to a new chat with Claude:

1. the new **PDF**;
2. **this .md file**;
3. *(optional but recommended)* the **previous finished HTML** (`uppsc-prelims-2025-notes.html`), so the same design, search, navigation and recall features can be reused without rebuilding them.

Then send the prompt in **Section 1**.

---

## 1. The prompt to paste

> Follow the attached playbook exactly to convert the attached PDF into handwritten-style HTML revision notes, with diagrams and active recall.
> **Completeness is the top priority: every fact in the PDF must appear in the notes.** That means every name, date, number, definition, list item, table row, example, footnote, caption and diagram label.
> Reuse the design and code of the attached previous HTML file if one is provided.
> Use at most 2 helper agents. Deliver one self-contained offline HTML file, plus the coverage report.

Optional extras to add to the prompt:

- *"Exam: ___ (e.g. UPSC / SSC / NEET)"* – shapes the recall questions.
- *"Language: keep Hindi terms in brackets"* – for bilingual PDFs.
- *"White paper background with light texture"* – the final look used last time.

---

## 2. Output requirements (the spec)

### 2.1 Structure

- Organise as **Subject → Chapter → Topic → Subtopic**, using the PDF's real headings.
- Every unit carries `data-pages` with the **PDF page numbers** (the PDF file's page index, not the printed number), e.g. `"5"`, `"5–6"`, `"12, 15"`.
- Use unique, stable ids: lowercase-kebab with a subject prefix, e.g. `anc-jain-tirthankaras`.
- Do not create empty sections.

### 2.2 Content rules

1. **Preserve everything.** This includes names, dates, numbers and units, definitions, classifications, examples, comparisons, complete lists (all 24 of 24, all 11 of 11), table rows, notes and footnotes, image or diagram labels, and map labels.
2. **Merge genuine repetition only.** Keep every unique detail, and list all source pages in `data-pages`. When repeated copies **disagree**, show both versions.
3. **Write clear, concise English**, keeping the exam terminology.
4. **Never invent facts.** The only allowed additions are:
   - a 1–2 sentence lead explaining the central idea;
   - memory aids, labelled **"Learning aid – not from source"**;
   - "Remember" and "Common confusion" notes built from source facts;
   - **Source check** flags.
5. **Garbled or machine-translated text:** write the correct term only when it is certain, and add a Source check flag that shows the source wording.
6. **Doubtful, conflicting or outdated claims:** keep the source claim and add a flag. Never change it silently.
7. **Preserve time context**, e.g. "as per source, 2025", "Census 2011".
8. **Exclude** headers, footers, watermarks, adverts, phone numbers and contact details.

### 2.3 Visual style (handwritten notebook)

- **Paper:** white paper with a light paper grain (inline SVG noise, no image files), subtle ruled lines and a red margin line.
- **Fonts:** local handwriting-style stacks with no downloads.
  - Body: `"Kalam","Patrick Hand","Comic Neue","Segoe Print","Bradley Hand","Chalkboard SE","Comic Sans MS","Coming Soon",casual,sans-serif`
  - Headings: `"Caveat","Kalam","Segoe Print","Bradley Hand","Chalkboard SE","Marker Felt","Comic Sans MS","Coming Soon",casual,"Dancing Script",cursive`
- **Ink colours:** blue/near-black text, muted red headings, restrained yellow highlighter (`<mark>`).
- **Hand-drawn touches:** underlines, outlined note boxes (Remember ★, Common confusion ⚠, Learning aid ✿, Source check ⚑, Recap ↺), and occasional margin notes.
- **Diagrams** use a simple sans font so their labels stay readable.
- **Text must stay selectable and searchable.** Never put text inside images.

### 2.4 Navigation and features (lightweight inline JavaScript)

- **Contents and navigation**
  - Sticky table of contents in a sidebar, with expandable subjects and chapters, plus "Open all / Close all" buttons.
  - A drawer menu on mobile.
  - An active-topic indicator in the sidebar.
  - Breadcrumbs.
  - A back-to-top button.
  - Expand-all / collapse-all for the notes.
  - A page tag (`p. 12`) on every heading.
- **Global search**
  - Covers headings, notes, diagrams and recall questions. Answers are excluded, so search doesn't spoil them.
  - Each result shows the title, its path and a highlighted excerpt.
  - Clicking a result opens any collapsed section or recall block, turns diagram labels back on if needed, scrolls to the match and highlights it.
- **Diagrams**
  - **Chapter map:** opens every chapter; its boxes link to the chapter's topics.
  - **Topic diagrams:** each has a title, a one-sentence takeaway, and a Hide/Show labels button where it suits a label test.
- **Recall**
  - **Test your memory:** in every topic, 3–5 questions, with answers hidden until "Reveal answer".
  - **Chapter recap:** closes every chapter.
- **Index of source checks:** at the end, auto-built and linked to each flag.
- **Print**
  - Expands everything and hides the navigation.
  - Starts each subject on a new page and never splits a diagram.
  - Moves the answers into a separate **answer key** at the end.

### 2.5 Diagram rules

Match each kind of information to a fitting visual:

| Information | Visual |
|---|---|
| Chronology | Timeline; **parallel lanes** for overlapping rulers or periods |
| Hierarchy / classification | Tree |
| Process / cause → effect | Numbered flowchart (arrows only when the source supports the order) |
| Truly repeating process | Cycle |
| Easily confused concepts | Comparison matrix with ◆ marking the decisive differences |
| People / books / places | Aligned table or grouped cards |
| Location | Compass schematic marked "Schematic – not to scale"; never invent boundaries |
| Structure / parts | Layer diagram |
| Numbers | Bar chart from the source's values only, starting at zero |

General rules:

- Show one relationship per diagram, and split crowded ones.
- If a visual groups a list, it must include every entry.
- Mark conflicting facts with ⚑ in the visual too.
- Use restrained colours that still read in grayscale.

---

## 3. Workflow (step by step)

### Step 1 – Inventory the whole PDF before writing anything

```bash
mkdir -p work/pages
for i in $(seq 1 N); do pdftotext -f $i -l $i input.pdf work/pages/p$(printf %03d $i).txt; done
```

- Find subject and chapter boundaries by grepping for headings. Then **look at the page images** of the boundary pages: cover pages, blank pages and section dividers often hide there.
- Make a **page ledger** (`ledger.md`) with one line per page: `page → subject → main headings → type (content / cover / blank / advert)`.
- Flag pages whose text comes out **jumbled**: two-column interleaving, tables, timelines, boxes, diagrams. These pages **must be read from the page image** (Read tool with `pages:` ≤ 20 per call), in visual order: left column top→bottom, then right column.

### Step 2 – Split the work

- Divide by subject so that each worker gets about 150–200k characters of source text.
- Each worker writes one fragment file per subject (`frag/NN-code.html`), following Section 2 exactly, plus a **coverage file** (`NN-code.coverage.txt`) that lists page → topic ids and every flag added.
- Fragments contain only `<section class="subject">…</section>`, with no `<html>`, `<style>` or `<script>`.

**Fragment skeleton**

```html
<section class="subject" id="anc" data-title="Ancient Indian History" data-pages="3–17">
  <h2>Ancient Indian History</h2>
  <section class="chapter" id="anc-religions" data-title="Jainism &amp; Buddhism" data-pages="3–6">
    <h3>Jainism &amp; Buddhism</h3>
    <article class="topic" id="anc-jain-tirthankaras" data-title="24 Tirthankaras" data-pages="5">
      <h4>24 Tirthankaras of Jainism</h4>
      <p class="lead">…</p>
      <ol class="b">…all 24…</ol>
      <section class="subtopic" id="anc-jain-symbols" data-title="Symbols" data-pages="5–6"><h5>…</h5>…</section>
    </article>
  </section>
</section>
```

**Content elements:**

- `<p class="lead">`
- `<ul class="b">` / `<ol class="b">`
- `<dl class="terms">`
- `<table class="t">`
- `<ol class="timeline"><li><span class="when">1919</span> …</li></ol>`
- `<div class="flow"><span>…</span></div>`
- `<div class="note remember|confusion|aid|flag|recap"><b>Label</b> …</div>`
- `<aside class="margin">`
- `<mark>`

### Step 3 – Add visuals and recall (a second pass, insert only)

- First freeze the notes: `cp -r frag frag_v1`.
- **Insert only.** Never edit existing notes in this pass. A checker strips the inserted elements and compares the rest with `frag_v1`.
- Per chapter: one **chapter map** (`figure.viz.overview`, id `<chapter>-map`) right after the `<h3>`, and one **recap** (`div.note.recap.chrecap`) as the chapter's last child.
- Per topic: one `details.recall` block as the topic's last child, with 3–5 questions.
- Mix question types: recall a fact, explain a difference, reconstruct a sequence, fill in a missing diagram label, explain a relationship in one sentence.
- Every answer gets a `<span class="src">p. N</span>` page reference.

**Component markup** (the renderer CSS/JS supports these classes):

```html
<figure class="viz" id="TOPIC-fig1" data-labels>
  <figcaption><span class="vt">Title</span><span class="tk">One-sentence takeaway.</span></figcaption>
  <!-- one of: -->
  <ol class="htl"><li><span class="d">1919</span><span class="e">Rowlatt Act</span></li></ol>
  <div class="lanes" style="--start:1200;--end:1800"><div class="axis"><span style="--t:1200">1200</span>…</div>
    <div class="lane"><span class="ln">Delhi Sultanate</span><div class="track"><span class="bar" style="--a:1206;--b:1526">1206–1526</span></div></div></div>
  <ul class="tree"><li><span>Root</span><ul><li><span>Child</span></li></ul></li></ul>
  <ol class="steps"><li><b>Step</b><span>detail</span></li></ol>   <!-- add class "cycle" only if it truly repeats -->
  <table class="t cmp">… <td class="key">decisive difference</td> …</table>
  <div class="cards"><div class="card"><div class="ch">Group</div><ul><li>…</li></ul></div></div>
  <div class="bars" style="--max:3907" data-unit="leopards"><div class="brow" style="--v:3907"><span class="bk">MP</span><span class="bt"><span class="bb"></span></span><span class="bv">3,907</span></div></div>
  <div class="layers"><div class="layer"><b>Crust</b><span>…</span></div></div>
  <div class="compass"><div class="c-n">…</div><div class="c-c">Centre</div>…</div>
  <p class="vnote">Schematic – not to scale.</p>
</figure>

<details class="recall"><summary>Test your memory</summary><ol class="qs">
  <li><p class="q">Question?</p><div class="a"><p><b>Answer.</b> Explanation. <span class="src">p. 12</span></p></div></li>
</ol></details>
```

- Hideable label words go inside `<span class="lbl">…</span>`.
- Uncertain or conflicting facts go inside `<span class="unc">…</span>`, which renders with ⚑.

### Step 4 – Assemble

- **If the previous HTML is attached:** use it as the shell. Delete everything from the first `<section class="subject"` up to `<section class="appendix" id="source-checks"`, put the new fragments there, and update the cover text (title, source name, notes on cover and blank pages).
- **If it isn't attached:** build the shell to Section 2.4.
- Concatenate the fragments in subject order to make one HTML file.

### Step 5 – Completeness check (do not skip)

Run this token-coverage check. It compares every source page's numbers and capitalised words with the finished notes:

```python
# coverage.py  —  python3 coverage.py FIRST LAST THRESHOLD
import re, sys, html, glob
JUNK = re.compile(r"(?im)^.*(made with|contact us|click here|watermark).*$|\d{10}")   # adapt to the PDF's headers/footers
STOP = set("The This These It In On Of And Or For To From With By At As An Is Are Was Were Be Which Who When Where What Note Example Important Major Other First Some All Most Related Year Total".split())
def toks(s):
    nums = {n.rstrip(".,") for n in re.findall(r"\b\d[\d,\.]*\b", s) if len(n.rstrip(".,")) >= 2}
    words = {w for w in re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", s) if w not in STOP}
    return nums | words
notes = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8").read())) for f in sorted(glob.glob("frag/*.html")))
nn = re.sub(r"\s+", " ", notes).lower(); nc = nn.replace(",", "")
lo, hi, thr = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
for p in range(lo, hi + 1):
    t = JUNK.sub("", open(f"pages/p{p:03d}.txt", encoding="utf-8").read()); tk = toks(t)
    if not tk: continue
    miss = sorted(x for x in tk if x.lower() not in nn and x.lower().replace(",", "") not in nc)
    if 1 - len(miss)/len(tk) < thr: print(f"p{p}: missing {', '.join(miss[:40])}")
```

- Run `python3 coverage.py 1 LAST 0.95`. For **every missing token**, open that page and either add the fact or confirm it is a spelling normalisation, header or advert.
- Repeat until the only remaining "misses" are explained.
- Then **re-read the image of every jumbled page** against the notes, one by one. Tables and timelines are where facts usually go missing.
- Count list lengths: if the source says "17 goals", "18 reserves" or "24 Tirthankaras", count the items in the notes.
- Write `coverage-report.md` covering:
  - which pages are content, cover or blank;
  - the result of the token check;
  - every remaining explained miss;
  - every Source check flag.

### Step 6 – Structural and browser checks

Run the structural checks:

- Valid nesting.
- Unique ids, with no broken `#links`.
- Every unit has a heading, a page tag and an entry in the contents.
- Every chapter has one chapter map whose links cover all its topics exactly once, plus one recap.
- Every topic has 3–5 recall questions.
- Every diagram has a title and a takeaway.
- Bars use zero to max.
- Lanes have start < end.
- Timelines run in order (BCE years are negative numbers).
- **The insert-only diff against `frag_v1` passes.**

Then the Playwright browser checks:

- No console errors and no external network requests.
- No sideways scrolling at 360, 768, 900 or 1280 px.
- Search for 4–5 terms. Each click on a result must reveal collapsed content, show the highlighted match on screen, and update the breadcrumbs and active topic.
- In the mobile drawer, it opens, and clicking a link closes it.
- Hide labels makes them invisible (`visibility:hidden`), not just faded.
- Print to PDF:
  - every section is expanded;
  - inline answers are hidden;
  - the answer key is present;
  - no diagrams are clipped. Spot-check 3–4 pages as images.

### Step 7 – Deliver

- Send the single HTML file. It works offline, with no fonts, libraries or images to download.
- Send `coverage-report.md` alongside it.
- Summarise briefly: counts, flags, and any doubtful facts that are worth correcting.

---

## 4. Completeness checklist (tick before delivering)

- [ ] Every content page appears in some unit's `data-pages`, and cover, blank and advert pages are listed in the report.
- [ ] Every jumbled page was read from its image.
- [ ] The token coverage is ≥ 95% on every content page, and every miss is explained.
- [ ] Stated list counts match the item counts in the notes.
- [ ] Repeated sections were merged with no unique detail lost, and conflicts are shown both ways and flagged.
- [ ] Footnotes, "Note:" lines, examples, captions and diagram labels are all included.
- [ ] No placeholders, "etc.", "…and more" or summary-only bullets were introduced.
- [ ] Time-sensitive facts carry their source date, and outdated ones are flagged.
- [ ] No headers, footers, adverts or phone numbers leaked in.

---

## 5. Lessons from last time

- **Two-column PDFs:** `pdftotext` without `-layout` reads column by column, but tables, timelines and boxes still come out scrambled. Always read those from the page images.
- **Machine-translated sources** have systematic garbles: "Congratulations" means Abhinandannath, and "Gemini" means Jaimini. Correct only when certain, and always show the source wording.
- **Section cover pages** sit between subjects. Check the boundary pages visually, or the page ranges will be off by one.
- **Agents tend to "fix" old notes** during the visual pass. Freezing `frag_v1` and running the insert-only diff stops this.
- **Search clicks:** ignore clicks on results in the global anchor handler, or the page jumps back to the top of the topic after highlighting.
- **Timelines with many items:** give them `overflow-x:auto` so they don't widen the page at about 900 px.
- **Layer shading:** keep it light (lightness 97% minus about 2.6% per step) so text stays readable.
- **Page tags with long page lists:** they must be allowed to wrap, or they overflow on phones.
