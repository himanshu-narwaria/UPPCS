# Writer brief: memory layer for Drishti Current Affairs 2026 (2), UPPCS level

Folder: `dashboard-src/subjects/current_affairs/` (all paths below are relative to it).

You turn study units of a current-affairs magazine into short, easy-to-memorise material for a
UPPCS (Uttar Pradesh PCS) aspirant. The student is bilingual; English is the main language.
Code builds the web pages from your JSON. The original text is shown in full on the page anyway,
so your job is to make it **learnable**, not to copy it.

## Input
`packs/<you>.txt` lists your units. Each starts with a line like
`[u0396] Ch4 · Strategic Restructuring of IDBI Bank`, then a context line and the source text.
`**bold**` marks the words the magazine itself printed in bold (its key facts). Tables are `| a | b |`.
Chapter 1 units are "stories": a dated question plus follow-ups, written `Q…: question => A: answer`.
Read every unit in full. Do not skip any.

## Output
Write JSON files `memory/<you>.part01.json`, `memory/<you>.part02.json`, … each a JSON object
`{ "u0396": {…}, "u0397": {…} }` with at most about 50 units per file, so no single write is huge.
Every unit id in your pack must appear exactly once across your parts.

### Article and news-item units (chapters 2-10)
```json
"u0396": {
  "gist": "One sentence, max 25 words, plain English: what happened + why it matters.",
  "facts": ["3-6 lines, max 18 words each: the exam-worthy facts (who, what, where, when, how much)."],
  "hook": "Optional memory aid. Say what it encodes. e.g. 'IDBI 60.72 → Govt 30.48 + LIC 30.24: two near-30s add to ~61'.",
  "trap": "Optional: 'Don't confuse X with Y' when two similar facts could be mixed up.",
  "hindi": ["Strategic disinvestment (रणनीतिक विनिवेश)"],
  "priority": 1,
  "mcq": [{"q": "Which company was approved in October 2026 as the buyer for a 60.72% stake in IDBI Bank?",
           "o": ["10955230 Canada Inc.", "Fairfax India Holdings", "Life Insurance Corporation", "Emirates NBD"],
           "k": 0, "why": "CCEA approved 10955230 Canada Inc. (parent: Fairfax Financial Holdings)."}]
}
```
### Story units (chapter 1 only)
```json
"u0001": {
  "line": "Max 30 words: the whole story compressed, e.g. 'National Urban Conclave 2026 (25 Oct) → Bhubaneswar; focus: urban governance for Viksit Bharat 2047'.",
  "hook": "", "trap": "", "hindi": [], "priority": 1
}
```
Story units get no `facts` and no `mcq` (code makes their MCQs from the book's own answers).

## Rules (strict)
1. **Use only the unit's own text.** Never add outside knowledge, updates or background. If the
   source contradicts itself or looks wrong, keep it and add `"check": "what looks wrong"`.
2. **Copy every name, number, date, rank, amount and place exactly** as the source has it. The
   validator rejects any number of two or more digits that is not in that unit's source text.
3. **Simple English**: short sentences, everyday words, no jargon without a 2-3 word explanation.
4. **Facts first, exam angle**: prefer what UPPCS asks: who launched/released/chaired, where,
   when, rank, first/largest, amount, theme, host, winner, ministry/organisation, state.
5. **Memory aids only where they truly help** (about one unit in three): acronym expansion,
   number links, rhymes, vivid pictures, "pairs" (place–state, award–person). Never force one.
   A hook must be correct and must not introduce new facts.
6. **trap** only for real confusion risks (similar names, two ranks, edition vs year, launched vs expanded).
7. **hindi**: 0-3 standard Hindi terms you are sure of, as `English (हिंदी)`. Skip names of people/places.
8. **priority**: 1 = must-know for UPPCS (anything about Uttar Pradesh; central schemes/policies/
   laws; indices and India's rank; "first" or record facts; major summits and India's role;
   key appointments; major awards). 2 = useful. 3 = low value (minor foreign events, routine
   items). Bihar chapter: priority 3 unless it involves a central scheme or national first.
9. **mcq**: 1 question per unit (2 only for long, fact-rich units; 0 for units with nothing
   testable). UPPCS style: one clear correct answer from the source; three plausible wrong
   options of the same type (cities with cities, numbers with numbers, ministries with
   ministries) that the source shows are wrong or that are clearly not the answer; no "all/none
   of the above"; vary the correct position (k = 0-3); the stem must make sense on its own
   (name the event and year). `why` = max 20 words citing the fact.
10. Valid JSON only: double quotes, no trailing commas, escape inner quotes.

## Check before you finish
Run `python ca_validate_memory.py <you>` from this folder and fix every ERROR. Repeat until it
prints 0 errors. Warnings are single-digit numbers; check them, they may be fine.
