"""Rebuild all three Indian History UPPSC files from the extracted PDF text in one command:
1. history-uppsc-full-notes.html
2. history-uppsc-quick-notes.html
3. history-in-72h.html

Usage:
    python dashboard-src/subjects/history/rebuild_all_history.py
"""
import sys, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_history_data
import build_structured_chapters
import build_repeated_and_latest
import generate_full_notes
import generate_quick_notes
import generate_72h_plan

def rebuild():
    t0 = time.time()
    print("--- 1/6: Parsing all chapters & UPPSC questions ---")
    build_history_data.parse_all_chapters()

    print("--- 2/6: Structuring chapters, focus & topics ---")
    build_structured_chapters.build_all_structured_chapters()

    print("--- 3/6: Building repeated facts & latest UPPSC ledger ---")
    build_repeated_and_latest.build_repeated_and_latest()

    print("--- 4/6: Generating history-uppsc-full-notes.html ---")
    generate_full_notes.generate_full_notes()

    print("--- 5/6: Generating history-uppsc-quick-notes.html ---")
    generate_quick_notes.generate_quick_notes()

    print("--- 6/6: Generating history-in-72h.html ---")
    generate_72h_plan.generate_72h_plan()

    print(f"\nAll three Indian History files successfully rebuilt in {time.time() - t0:.2f}s!")

if __name__ == "__main__":
    rebuild()
