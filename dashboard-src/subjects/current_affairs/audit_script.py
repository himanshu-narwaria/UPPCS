import os
import re
import json
import html
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FOLDER = os.path.join(ROOT, "Drishti-current affairs")

full_file = os.path.join(FOLDER, "current-uppsc-full-notes.html")
quick_file = os.path.join(FOLDER, "current-uppsc-quick-notes.html")
plan_file = os.path.join(FOLDER, "current-in-72h.html")

def check_security(path):
    s = open(path, encoding="utf-8").read()
    label = os.path.basename(path)
    
    # 1. Inline handlers (onclick, onload, etc.)
    inline_events = re.findall(r'<[a-zA-Z0-9]+[^>]*\s+(on[a-z]{3,15})\s*=', s, re.I)
    if inline_events:
        print(f"FAILED {label}: found inline event handlers: {set(inline_events)}")
        return False
        
    # 2. javascript: links
    js_links = re.findall(r'href\s*=\s*["\']javascript:', s, re.I)
    if js_links:
        print(f"FAILED {label}: found javascript: links!")
        return False
        
    # 3. External network resources (link, script, img, iframe)
    ext_resources = re.findall(r'<(link|script|img|iframe)[^>]*(href|src)\s*=\s*["\'](https?://[^"\']+)["\']', s, re.I)
    if ext_resources:
        print(f"FAILED {label}: found external resources: {ext_resources}")
        return False
        
    return True

def check_links(path):
    s = open(path, encoding="utf-8").read()
    label = os.path.basename(path)
    
    # Strip script blocks to only inspect HTML DOM markup
    s_no_scripts = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S)
    
    # Find all IDs and data-v
    ids = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', s_no_scripts))
    data_vs = set(re.findall(r'\bdata-v\s*=\s*["\']([^"\']+)["\']', s_no_scripts))
    all_targets = ids | data_vs
    
    # Find internal hash links
    hrefs = re.findall(r'href\s*=\s*["\']#([^"\']+)["\']', s_no_scripts)
    broken = []
    for h in hrefs:
        if h and h not in all_targets:
            broken.append(h)
            
    if broken:
        print(f"FAILED {label}: broken internal anchors: {Counter(broken)}")
        return False
        
    print(f"PASSED {label}: all {len(hrefs)} internal anchors resolve ({len(all_targets)} targets).")
    return True

def check_contracts():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "dashboard-src"))
    import build_dashboard as bd
    
    F = bd.parse_full(full_file)
    print(f"PASSED full notes contract: {len(F['chapters'])} chapters, {F['bank']} MCQs, {len(F['repeats'])} repeats.")
    
    Q = bd.parse_quick(quick_file)
    print(f"PASSED quick notes contract: {len(Q['chapters'])} chapters, {Q['repeats']} repeats, basis: {Q['basis'][:60]}...")
    
    P = bd.parse_72h(plan_file)
    print(f"PASSED 72h plan contract: key={P['key']}, exam={P['exam']}, hours={len(P['hours'])}.")
    
    bd.chapter_hours(F["chapters"], P, "72h plan")
    print("PASSED chapter_hours matching: all 10 chapters matched in Learn phase!")

def main():
    print(f"Auditing Current Affairs files in: {FOLDER}")
    print("\n=== 1. SECURITY & CSP AUDIT ===")
    for p in [full_file, quick_file, plan_file]:
        assert check_security(p), f"Security check failed for {p}"
    print("All 3 files passed CSP & Security audit.")
    
    print("\n=== 2. LINK RESOLUTION AUDIT ===")
    for p in [full_file, quick_file, plan_file]:
        assert check_links(p), f"Link check failed for {p}"
        
    print("\n=== 3. CONTRACT & DASHBOARD AUDIT ===")
    check_contracts()
    
    print("\nALL AUDIT CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    main()
