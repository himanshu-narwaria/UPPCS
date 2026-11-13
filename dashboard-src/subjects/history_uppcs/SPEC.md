# History-UPPCS: fact-extraction spec

Goal: for each chapter of the book "Ghatna Chakra Preview: Indian History 2026", list **every fact** found in that chapter (its explanation paragraphs, its questions with their keyed answers, and the answer explanations) as one clean fact list, so a UPPCS aspirant can revise the whole chapter in one reading. Completeness comes first: a fact that is in the chapter must be in the list. Nothing from outside the chapter may be added.

## Input
- `texts/chN.txt`: the full text of chapter N. It starts with an EXPLANATION SECTION (facts begin with `*`), then QUESTIONS: each has its number, stem, options (a)–(d), exam labels, `Ans. (x)`, then the answer explanation (tables appear as rows with ` | ` between cells). `[See the explanation of question K]` means the explanation is under question K.
- `qlist/chN.txt`: every question of chapter N, one per line: `item number | exam labels | Q: stem | KEY: keyed answer text`. Some lines end with `REVIEW: … do not tag`.
Read each of your chapter texts in full, top to bottom. Do not use the web.

## Output: `out/chN.md` (UTF-8), in EXACTLY this line format
```
@ N | <Chapter title>
## <Topic title>
- A fact with **key term**.
- A fact that questions tested. {12}
- A fact tested by several questions. {3,17,41}
! A caution taken from the book itself.
| Column | Column |
| cell | cell {8} |
```
- `@` exactly one, first line. `##` topic headings: short plain words, in the order the chapter teaches them; as many topics as the chapter needs.
- `-` one fact per line. `|` table rows: first row of a run is the header, equal cell counts in a run, no `---` row. Use a table when facts are naturally tabular (ruler → dynasty and dates, book → author, site → find, battle → year and sides, session → year, place and president, movement → leader and year, Governor-General → events).
- `!` caution: only when the book's own text says a key is disputed, wrong or outdated. Never from your own knowledge.
- No other line types, no blank-line prose, no nested bullets.

## What counts as a fact, and completeness
1. Take facts from all three places: the explanation paragraphs, the questions (stem + keyed answer; also true statements inside multi-statement questions, and what the wrong options actually are when the explanation says so), and the answer explanations.
2. Keep every name, date and year, place, ruler and dynasty, title, book and author, site and find, battle, treaty, Act, session and president, newspaper and editor, organisation and founder, slogan, number, first/last, list member. Lists stay complete; never write "etc.".
3. State each fact once. When the paragraph, several questions and explanations give the same fact, merge them into one line holding every detail. Do not drop a detail to merge.
4. Rewrite into very simple, short English (one fact per line, about 8–20 words; telegraphic style with `=`, `→`, `:` is fine). Compress wording, never content. Never write "Q", option letters, "the key says" or "the book says" in a fact line.
5. Do not add, correct or update anything from memory. If the chapter prints a date-bound fact ("at present", "recently"), keep its date.
6. There is no length limit. A long chapter gives a long list.

## Tags: which questions tested a fact
- For every question in `qlist/chN.txt` (all exams), put its item number in the `{…}` tag at the end of the ONE line that states the fact its keyed answer rests on. Several questions on the same fact share one line: `{3,17,41}`. This is how repeated facts are counted, so same-fact questions must share a line.
- Every non-REVIEW item number appears exactly once in the file. Questions marked REVIEW are not tagged, but facts stated clearly in their explanations are still listed.
- A matching or multi-statement question is tagged on the line of its main tested fact; its other statements still become their own fact lines (untagged, or tagged by other questions).

## Check before finishing
Run `python -I check.py N` in this folder for each of your chapters and fix everything it reports (missing, duplicate or unknown item numbers; bad line types; uneven tables). Then do your own completeness pass: reread the chapter text once more against your file and add any fact you missed.

## Final message (under 100 words)
Per chapter: number of fact lines and number of tagged items. Then anything you could not resolve. Do not paste the notes.
