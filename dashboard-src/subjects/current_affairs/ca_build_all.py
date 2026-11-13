"""Rebuild the three Current Affairs pages from the PDF in one command.

    python ca_build_all.py

Steps (each script can also run on its own):
  1. ca_extract.py          PDF -> ca_source.json   (questions light / answers bold, articles, tables)
  2. ca_structure.py        -> ca_units.json, packs/  (study units; text for the writer agents)
  3. ca_validate_memory.py  memory/*.json (the writers' memory cards) still match the units
  4. ca_render.py           -> the three HTML pages in "Drishti-current affairs/"
  5. ca_verify.py           every Q&A, text block and bold fact present; dashboard accepts the pages
  6. ../../build_dashboard.py  dashboard, site navigation and security headers
  7. ../../verify_study_updates.py  links, anchors, script syntax, CSP hashes

Reviewed inputs (data, not code): story_overrides.json fixes the few chapter-1 story boundaries the
grouping rule gets wrong; ca_extract.DRIFTED_TABLE_PAGES lists the tables printed out of line with
their own borders.

The memory cards in memory/ were written once by writer agents from packs/ (see memory/BRIEF.md);
they are inputs here, not regenerated. unit_ids.json keeps every unit's id stable across rebuilds
(keyed by chapter, kind, parent article and title), so an extraction fix changes only the content
of the units it touches; ca_validate_memory.py then shows which memory cards need a re-write.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DASH = HERE.parents[1]

STEPS = [
    (HERE, ["ca_extract.py"]),
    (HERE, ["ca_structure.py"]),
    (HERE, ["ca_validate_memory.py"]),
    (HERE, ["ca_render.py"]),
    (HERE, ["ca_verify.py"]),
    (DASH, ["build_dashboard.py"]),
    (DASH, ["verify_study_updates.py"]),
]


def main():
    t0 = time.time()
    for cwd, cmd in STEPS:
        print(f"\n>>> {cmd[0]}")
        r = subprocess.run([sys.executable, *cmd], cwd=cwd, text=True, encoding="utf-8", capture_output=True)
        out = (r.stdout or "").strip()
        if out:
            print("\n".join(out.splitlines()[-12:]))
        if r.returncode:
            print((r.stderr or "").strip()[-3000:])
            sys.exit(f"FAILED at {cmd[0]}")
    print(f"\nAll Current Affairs pages rebuilt and verified in {time.time() - t0:.0f}s.")


if __name__ == "__main__":
    main()
