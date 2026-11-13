import subprocess
import sys
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))

def run_step(script_name, runtime=None):
    script_path = os.path.join(HERE, script_name)
    print(f"\n>>> Running {script_name}...")
    t0 = time.time()
    res = subprocess.run([runtime or sys.executable, script_path], capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"FAILED {script_name}:\n{res.stderr}")
        sys.exit(1)
    if res.stdout.strip():
        print(res.stdout.strip())
    print(f"Finished {script_name} in {time.time() - t0:.1f}s")

def main():
    t_start = time.time()
    print("==================================================")
    print("  REBUILDING ALL CURRENT AFFAIRS STUDY FILES      ")
    print("==================================================")
    
    raw_pages = os.path.join(HERE, "raw_pages.json")
    if not os.path.exists(raw_pages):
        run_step("extract_all_pages.py")
        
    run_step("build_exact_chapter_boundaries.py")
    run_step("build_current_affairs_data.py")
    run_step("build_practice_and_repeats.py")
    run_step("build_template_assets.py")
    run_step("generate_full_notes.py")
    run_step("generate_quick_notes.py")
    run_step("generate_72h_plan.py")
    run_step("audit_script.py")
    run_step("critic_verify.py")
    run_step("runtime_verify.js", "node")
    run_step("build_coverage_audit.py")
    
    print("\n==================================================")
    print(f"ALL CURRENT AFFAIRS FILES REBUILT & VERIFIED ({time.time() - t_start:.1f}s)!")
    print("==================================================")

if __name__ == "__main__":
    main()
