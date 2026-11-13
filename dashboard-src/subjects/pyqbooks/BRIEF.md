# Writer brief: memory cards for past-paper books (UPPCS level)

You turn past exam questions from a chapterwise solved-paper book (Indian Polity, Indian History,
Economy, General Geography or General Science) into short, easy-to-memorise cards for a UPPCS (Uttar Pradesh PCS) aspirant. The student
reads English; Hindi terms help. The web pages show the full question, options, answer and the
book's explanation anyway, so your card is the **fact to remember**, not a copy of the question.

## Input
`<book>/packs/wNN.txt` (book = polity, history, economy, geography or science). Each entry is one
*fact cluster*:

```
[06-012] Ch6 · Parts of the Indian Constitution · asked in 2 paper(s): U.P.P.C.S. (Pre) 2023; ...
Q: Which among the following (Provision – Part of the Constitution) is not correctly matched?
Options: (a) Official Language – Part XVII (b) ... (d) Tribunals – Part XI
Answer: (d) Tribunals – Part XI
Also asked: <a similar question from another exam> -> <its answer>
Explanation: Tribunals are not mentioned in Part XI but in Part XIV (A) ...
```

The id in brackets (`06-012` = chapter 6, question 12; Geography also has `105-012`) is the card's
key. Read every entry; skip none.

Long statements and explanations are cut in the pack and end with "… [shortened in this brief; the
book continues]". That cut is ours, not the book's: never say the question or explanation is "cut
off", "garbled" or "incomplete" because of it.

## Output
JSON files `<book>/memory/wNN.part1.json`, `wNN.part2.json`, … (your writer number NN), each an
object `{ "06-012": {…}, "06-013": {…} }`, at most about 150 cards per file. Every id in your pack
must appear exactly once across your part files.

```json
"06-012": {
  "r": "Tribunals: Part XIV-A (Arts 323A, 323B), added by the 42nd Amendment, 1976, not Part XI (Centre-State relations).",
  "h": "Optional memory aid; say what it encodes.",
  "t": "Optional: Don't confuse Part X (Scheduled and Tribal Areas) with Part XI (Centre-State relations).",
  "hi": ["Tribunal (न्यायाधिकरण)"],
  "c": "Optional: only if the book's answer looks wrong or the question is garbled; say why."
}
```

### `r` – the Remember line (required)
* One statement of the fact the question tests, **max 30 words**, plain simple English, UPPCS level.
* Write the fact, not the question: "Regulating Act 1773 → Supreme Court at Calcutta (set up 1774; first CJ Elijah Impey)".
* Use "→", ";" and short phrases. Keep names, numbers, years, Articles exactly as in the entry.
* Statement / "which is correct" questions: state the true facts (and the false one if short).
* Match-the-list questions: give the correct pairs ("Board of Control → Pitt's India Act 1784; ...").
* "Not correctly matched" / "not true" questions: give the wrong pair and its correct form.
* When "Also asked" variants test a different angle of the same fact, cover them in the same line.
* If the answer is "not printed in the book", state the fact from the explanation if it settles it;
  otherwise write the question's fact as far as the entry supports and add a `c` note.

### `h`, `t`, `hi`, `c` (optional; add them only when they help)
* `h` memory aid: a real mnemonic, association or number trick (max 20 words). Not for every card;
  roughly one card in four.
* `t` trap: "Don't confuse X with Y" when the options hold a classic look-alike (max 25 words).
* `hi`: 0-2 key terms as "English (हिंदी)" in Devanagari. Use standard Hindi terms used in UPPCS
  Hindi papers (e.g. "Fundamental Rights (मौलिक अधिकार)", "Directive Principles (नीति निदेशक तत्व)").
* `c` ("Check", shown to students): only when the book itself looks wrong: the printed answer
  contradicts its own explanation, or (when you are certain) a fact the book states is outdated or
  wrong. Short; say what the book says and what is right. Students trust these notes, so:
  * "Answer: (a) …; (c) …" means the book prints two answers ("Ans. (a) & (c)"). Do not write that
    only one is printed.
  * "Answer: *" means the book says no option is fully correct. Write "The book gives no single
    answer (*)", not "answer not printed".
  * Never write a note about how the entry was extracted (merged lines, odd spacing, a cut text).
* Science and Geography: the page text loses subscripts and superscripts ("H O", "CO", "10 km").
  Write formulas and units correctly in your card (H2O, CO2, km², 10⁶) when the entry makes clear
  what is meant.

## Rules
* **Accuracy first.** Use only facts in the entry (question, options, answer, explanation). Do not
  add outside knowledge, dates or numbers. Every number of two or more digits you write must appear
  in that entry; a validator rejects cards that break this.
* Simple, exam-focused English. No filler ("It is important to note"). No markdown.
* Keep JSON valid (escape double quotes inside strings as \").
* Work in order through the pack and write each part file as you go (do not hold everything to the end).

## Check your work
Run `python pq_validate.py <book> wNN` from the folder `dashboard-src/subjects/pyqbooks/` and fix
every ERROR until it prints 0 errors. Warnings (single-digit numbers, long lines) are worth a look.
