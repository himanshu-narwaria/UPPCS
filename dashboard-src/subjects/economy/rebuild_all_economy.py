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
    if res.stdout.strip():
        print(res.stdout.strip())
    print(f"Finished {script_name} in {time.time() - t0:.1f}s")

def main():
    t_start = time.time()
    print("==================================================")
    print("     REBUILDING ALL ECONOMY STUDY FILES           ")
    print("==================================================")
    
    run_step("extract_repeats.py")
    run_step("extract_toc.py")
    run_step("extract_fonts.py")
    run_step("build_template_css.py")
    run_step("build_template_js.py")
    run_step("generate_quick_notes.py")
    run_step("audit_script.py")
    run_step("critic_verify.py")
    
    print("\n==================================================")
    print(f"ALL ECONOMY FILES REBUILT & VERIFIED ({time.time() - t_start:.1f}s)!")
    print("==================================================")

if __name__ == "__main__":
    main()
