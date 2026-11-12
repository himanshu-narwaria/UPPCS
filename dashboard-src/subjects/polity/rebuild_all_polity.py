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
    print("     REBUILDING ALL INDIAN POLITY STUDY FILES     ")
    print("==================================================")
    
    raw_pages = os.path.join(HERE, "raw_pages.json")
    if not os.path.exists(raw_pages):
        run_step("extract_all_pages.py")
        
    run_step("build_polity_data.py")
    run_step("generate_chapters_1_21.py")
    run_step("generate_chapters_22_42.py")
    run_step("build_structured_chapters.py")
    run_step("build_repeated_and_latest.py")
    run_step("generate_full_notes.py")
    run_step("generate_quick_notes.py")
    run_step("generate_72h_plan.py")
    
    print("\n==================================================")
    print(f"ALL INDIAN POLITY STUDY FILES REBUILT ({time.time() - t_start:.1f}s)!")
    print("==================================================")

if __name__ == "__main__":
    main()
