"""Rebuild active Polity artifacts from the unchanged source PDF and guides."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / "Indian_Polity_and_Governance" / "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf"


def run_step(name):
    started = time.time()
    print(f"Running {name}", flush=True)
    result = subprocess.run([sys.executable, str(HERE / name)], cwd=ROOT,
                            text=True, capture_output=True, encoding="utf-8")
    print(result.stdout.strip(), flush=True)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    print(f"Completed in {time.time() - started:.1f}s", flush=True)


def extraction_current():
    try:
        identity = json.loads((HERE / "source_identity.json").read_text(encoding="utf-8"))
        pages = json.loads((HERE / "raw_pages.json").read_text(encoding="utf-8"))
        return (identity["sha256"] == hashlib.sha256(PDF.read_bytes()).hexdigest()
                and len(pages) == identity["pages"]
                and all("columns" in page and "stream_text" in page for page in pages))
    except (OSError, ValueError, KeyError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reextract", action="store_true")
    arguments = parser.parse_args()
    if arguments.reextract or not extraction_current():
        run_step("extract_all_pages.py")
    for name in ("build_polity_data.py", "generate_chapters_1_21.py", "generate_chapters_22_42.py",
                 "build_structured_chapters.py", "build_repeated_and_latest.py", "generate_full_notes.py",
                 "generate_quick_notes.py", "generate_72h_plan.py", "critic_adversarial_qa.py"):
        run_step(name)
    print("Active Polity rebuild and evidence checks completed.")


if __name__ == "__main__":
    main()
