import subprocess
import sys
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))

def run_step(script_name):
    script_path = os.path.join(HERE, script_name)
    print(f"\n>>> Running {script_name}...")
    t0 = time.time()
    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"FAILED {script_name}:\n{res.stderr}")
        sys.exit(1)
    print(res.stdout.strip())
    print(f"Finished {script_name} in {time.time() - t0:.1f}s")

def main():
    t_start = time.time()
    print("==================================================")
    print("   REBUILDING ALL GENERAL GEOGRAPHY STUDY FILES   ")
    print("==================================================")
    
    # Check if raw_pages.json exists, if not extract it
    raw_pages = os.path.join(HERE, "raw_pages.json")
    if not os.path.exists(raw_pages):
        run_step("extract_all_pages.py")
        
    run_step("build_chapter_boundaries.py")
    run_step("find_exact_chapter_starts.py")
    run_step("update_titles.py")
    run_step("build_geography_data.py")
    run_step("build_repeated_and_latest.py")
    if os.path.exists(os.path.join(HERE, "generate_chapters_1_31.py")):
        run_step("generate_chapters_1_31.py")
    if os.path.exists(os.path.join(HERE, "generate_chapters_32_83.py")):
        run_step("generate_chapters_32_83.py")
    run_step("build_structured_chapters.py")
    run_step("generate_full_notes.py")
    run_step("generate_quick_notes.py")
    run_step("generate_72h_plan.py")
    
    print("\n==================================================")
    print(f"ALL GEOGRAPHY FILES SUCCESSFULLY REBUILT ({time.time() - t_start:.1f}s)!")
    print("==================================================")

if __name__ == "__main__":
    main()
