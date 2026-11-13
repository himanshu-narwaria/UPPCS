"""Rebuild the Polity, History, Economy, Geography and Science study pages from their PDFs in one command.

    python pq_build_all.py              (all five books)
    python pq_build_all.py polity       (one book)

Steps for each book (each script also runs on its own):
  1. pq_extract.py    PDF -> <book>/source.json: every question (bold), options, exam tags,
                      answer, explanation, and each chapter's theory, read by font and position
  2. pq_structure.py  -> <book>/clusters.json (one fact per cluster of repeated questions) and
                      <book>/packs/wNN.txt (what the writer agents read)
  3. pq_validate.py   the writers' memory cards in <book>/memory/ still match the clusters
  4. pq_render.py     -> the three HTML pages in the book's folder
  5. pq_verify.py     every question, option and answer present; dashboard parsers accept the pages
then ../../build_dashboard.py (dashboard, site navigation, security headers) and
../../verify_study_updates.py (links, anchors, script syntax, CSP hashes).

The memory cards were written once by writer agents from the packs (see BRIEF.md); they are
inputs here, not regenerated. Cluster ids are the book's own chapter and question numbers
("06-012"), so a re-run of the extraction keeps every card attached to its question.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DASH = HERE.parents[1]


def run(cwd, cmd):
    print(f"\n>>> {' '.join(cmd)}")
    r = subprocess.run([sys.executable, *cmd], cwd=cwd, text=True, encoding="utf-8", capture_output=True)
    out = (r.stdout or "").strip()
    if out:
        print("\n".join(out.splitlines()[-8:]))
    if r.returncode:
        print((r.stderr or "").strip()[-3000:])
        sys.exit(f"FAILED at {' '.join(cmd)}")


def main():
    t0 = time.time()
    books = sys.argv[1:] or ["polity", "history", "economy", "geography", "science"]
    for b in books:
        for step in (["pq_extract.py", b], ["pq_structure.py", b], ["pq_validate.py", b],
                     ["pq_render.py", b], ["pq_verify.py", b]):
            run(HERE, step)
    run(DASH, ["build_dashboard.py"])
    run(DASH, ["verify_study_updates.py"])
    print(f"\nRebuilt and verified {', '.join(books)} in {time.time() - t0:.0f}s.")


if __name__ == "__main__":
    main()
