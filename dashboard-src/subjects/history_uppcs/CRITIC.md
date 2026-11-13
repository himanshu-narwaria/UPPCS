# History-UPPCS: critic pass

You are the critic for fact lists that another agent extracted from a book. Read `SPEC.md` first: it defines what the lists must be. Your job is to find and fix what is wrong, not to praise.

For each of your chapters N, compare the source `texts/chN.txt` (read it in full) and `qlist/chN.txt` against `out/chN.md`, and fix `out/chN.md` directly:

1. **Missing facts.** Go through the chapter text section by section: every explanation paragraph, every question's keyed answer, every answer explanation. Any name, number, date, place, ruler, book, author, site, treaty, session, list member or definition that is in the source but not in the file: add it as a fact line under the right topic (or to an existing line or table).
2. **Unsupported facts.** Any fact line whose content is not in this chapter's source text (added from memory, "corrected", updated, or from another chapter): delete it or restore what the source says. `!` lines must come from the book's own remarks.
3. **Wrong facts.** Any line that misstates the source (wrong number, year, name, place, swapped pair): correct it to the source.
4. **Wrong tags.** A tag must sit on the line that states what that question's keyed answer rests on. Spot-check at least every third question; move tags that sit on the wrong line. Questions testing the same fact must share one line, so merge duplicate fact lines and combine their tags.
5. **Repetition and clarity.** Merge lines that state the same fact twice; rewrite lines that are unclear, too long, or use "Q", option letters or "the key says".

Rules: keep the SPEC line format; do not reorganise for its own sake; after editing a chapter run `python -I check.py N` and get OK.

Final message (under 150 words): per chapter, counts of facts added, removed, corrected and tags moved, plus the two or three most serious problems you found. Say plainly if a chapter was only partly checked.
