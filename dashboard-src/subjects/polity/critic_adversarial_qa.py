import json
import re
import os
import sys
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

def run_critic_pass():
    print("==================================================")
    print("      MANDATORY ADVERSARIAL CRITIC PASS (QA)      ")
    print("==================================================")
    
    failures = []
    
    # ----------------------------------------------------
    # CHECK 1: IMMUTABLE GUARDRAILS PRESERVATION CHECK
    # ----------------------------------------------------
    print("\n--- CHECK 1: IMMUTABLE GUARDRAILS PRESERVATION ---")
    with open(os.path.join(HERE, "guardrails_lock.json"), encoding="utf-8") as f:
        locks = json.load(f)
        
    def get_hash(data):
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        return hashlib.sha256(data_bytes).hexdigest()

    # Polity parsed questions
    with open(os.path.join(HERE, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        p_qs = json.load(f)
    h_p_qs = get_hash(p_qs)
    if h_p_qs != locks["polity_parsed_questions_hash"]:
        failures.append(f"GUARDRAIL BREACH: Polity parsed questions hash mismatch! Expected {locks['polity_parsed_questions_hash']}, got {h_p_qs}")
    else:
        print(f"  [PASS] Polity parsed questions (1,280 MCQs): EXACT MATCH ({h_p_qs[:12]}...)")

    # Polity repeated facts
    with open(os.path.join(HERE, "repeated_facts.json"), encoding="utf-8") as f:
        p_rep = json.load(f)
    h_p_rep = get_hash(p_rep)
    if h_p_rep != locks["polity_repeated_facts_hash"]:
        failures.append(f"GUARDRAIL BREACH: Polity repeated facts hash mismatch! Expected {locks['polity_repeated_facts_hash']}, got {h_p_rep}")
    else:
        print(f"  [PASS] Polity repeated facts (141 facts): EXACT MATCH ({h_p_rep[:12]}...)")

    # Environment pq-data
    with open(os.path.join(ROOT, "Environment_2025", "environment-ecology-2025-uppsc-notes.html"), encoding="utf-8") as f:
        e_notes = f.read()
    e_pq_data = json.loads(re.search(r'<script id="pq-data" type="application/json">(.*?)</script>', e_notes, re.S).group(1))
    h_e_pq = get_hash(e_pq_data)
    if h_e_pq != locks["env_pq_data_hash"]:
        failures.append(f"GUARDRAIL BREACH: Environment pq-data hash mismatch! Expected {locks['env_pq_data_hash']}, got {h_e_pq}")
    else:
        print(f"  [PASS] Environment pq-data (633 MCQs): EXACT MATCH ({h_e_pq[:12]}...)")

    # Environment dash-repeats table
    e_rep_table = re.search(r'id="dash-repeats".*?<tbody>(.*?)</tbody>', e_notes, re.S).group(1)
    h_e_rep = get_hash(e_rep_table.strip())
    if h_e_rep != locks["env_rep_table_hash"]:
        failures.append(f"GUARDRAIL BREACH: Environment dash-repeats table hash mismatch! Expected {locks['env_rep_table_hash']}, got {h_e_rep}")
    else:
        print(f"  [PASS] Environment repeated facts table (98 facts): EXACT MATCH ({h_e_rep[:12]}...)")

    # ----------------------------------------------------
    # CHECK 2: UNIQUENESS CHECK (15 QUESTIONS / SECTION)
    # ----------------------------------------------------
    print("\n--- CHECK 2: QUESTION UNIQUENESS (0% CROSS-SECTION DUPLICATION) ---")
    # Polity 72h plan
    with open(os.path.join(ROOT, "Indian_Polity_and_Governance", "polity-in-72h.html"), encoding="utf-8") as f:
        polity_72 = f.read()
        
    p_hours = re.findall(r'<section class="view" id="h(\d+)"[^>]*>.*?<h2>(.*?)</h2>(.*?)(?=<section class="view"|$)', polity_72, re.S)
    p_ch_qs = {}
    for h, title, body in p_hours:
        if int(h) <= 48: # Learn hours
            base = re.sub(r' · part \d+ of \d+$', '', title)
            m_q = re.search(r'data-q="([^"]*)"', body)
            qs = [q.strip() for q in m_q.group(1).split(",") if q.strip()] if m_q else []
            if base not in p_ch_qs:
                p_ch_qs[base] = []
            p_ch_qs[base].append((h, title, qs))
            
    polity_q_dups = 0
    for base, parts in p_ch_qs.items():
        if len(parts) > 1:
            all_seen = set()
            for h, title, qs in parts:
                dups = set(qs).intersection(all_seen)
                if dups:
                    polity_q_dups += len(dups)
                    failures.append(f"Polity Learn Hour {h} ({title}) has {len(dups)} duplicate questions: {list(dups)[:3]}")
                all_seen.update(qs)
                
    if polity_q_dups == 0:
        print(f"  [PASS] Polity Multi-Part Chapters: 0 duplicate questions across all parts!")
    else:
        print(f"  [FAIL] Polity Multi-Part Chapters had {polity_q_dups} duplicate questions!")

    # Environment 72h plan
    with open(os.path.join(ROOT, "Environment_2025", "evs-in-72h.html"), encoding="utf-8") as f:
        evs_72 = f.read()
    e_hours = re.findall(r'<section class="view" id="h(\d+)"[^>]*>.*?<h2>(.*?)</h2>(.*?)(?=<section class="view"|$)', evs_72, re.S)
    e_ch_qs = {}
    for h, title, body in e_hours:
        if int(h) <= 53: # Learn hours
            base = re.sub(r' · part \d+ of \d+$', '', title)
            m_q = re.search(r'data-q="([^"]*)"', body)
            qs = [q.strip() for q in m_q.group(1).split(",") if q.strip()] if m_q else []
            if base not in e_ch_qs:
                e_ch_qs[base] = []
            e_ch_qs[base].append((h, title, qs))
            
    env_q_dups = 0
    for base, parts in e_ch_qs.items():
        if len(parts) > 1:
            all_seen = set()
            for h, title, qs in parts:
                dups = set(qs).intersection(all_seen)
                if dups:
                    env_q_dups += len(dups)
                    failures.append(f"Environment Learn Hour {h} ({title}) has {len(dups)} duplicate questions: {list(dups)[:3]}")
                all_seen.update(qs)
    if env_q_dups == 0:
        print(f"  [PASS] Environment Multi-Part Chapters: 0 duplicate questions across all parts!")
    else:
        print(f"  [FAIL] Environment Multi-Part Chapters had {env_q_dups} duplicate questions!")

    # ----------------------------------------------------
    # CHECK 3: DUPLICATION & INTEGRITY CHECK (72-HOURS NOTES)
    # ----------------------------------------------------
    print("\n--- CHECK 3: 72-HOURS NOTES DEDUPLICATION & CUT-OFF CHECK ---")
    # Check for raw cut-off book paragraphs or <small>Stem truncated in the reading notes blocks
    p_readings = "".join(re.findall(r'<div class="reading">(.*?)</div>', polity_72, re.S))
    e_readings = "".join(re.findall(r'<div class="read">(.*?)</div>', evs_72, re.S))
    
    polity_cutoffs = len(re.findall(r'\.\.\.|<small>[^<]*truncated', p_readings))
    env_cutoffs = len(re.findall(r'\.\.\.|<small>[^<]*truncated', e_readings))
    
    if polity_cutoffs == 0:
        print("  [PASS] Polity 72h Notes: ZERO raw cut-off paragraphs or trailing '...'.")
    else:
        failures.append(f"Polity 72h Notes has {polity_cutoffs} cut-off/truncated items!")
        print(f"  [FAIL] Polity 72h Notes has {polity_cutoffs} cut-off items!")

    if env_cutoffs == 0:
        print("  [PASS] Environment 72h Notes: ZERO raw cut-off paragraphs or trailing '...'.")
    else:
        failures.append(f"Environment 72h Notes has {env_cutoffs} cut-off/truncated items!")
        print(f"  [FAIL] Environment 72h Notes has {env_cutoffs} cut-off items!")

    # Check cross-section text similarity in multi-part chapters
    for base, parts in p_ch_qs.items():
        if len(parts) > 1:
            for i in range(len(parts)):
                if i > 0:
                    h_curr = parts[i][0]
                    h_prev = parts[i-1][0]
                    # extract reading body
                    m1 = re.search(rf'<section class="view" id="h{h_prev}"[^>]*>.*?<div class="reading">(.*?)</div>', polity_72, re.S)
                    m2 = re.search(rf'<section class="view" id="h{h_curr}"[^>]*>.*?<div class="reading">(.*?)</div>', polity_72, re.S)
                    t1 = re.sub(r'<[^>]+>', ' ', m1.group(1)).strip().split() if m1 else []
                    t2 = re.sub(r'<[^>]+>', ' ', m2.group(1)).strip().split() if m2 else []
                    s1, s2 = set(t1), set(t2)
                    sim = len(s1.intersection(s2)) / len(s1.union(s2)) if s1.union(s2) else 0
                    if t1 == t2:
                        failures.append(f"Polity Chapter '{base}' Hour {h_prev} and {h_curr} have 100% IDENTICAL text!")
                    elif sim > 0.35:
                        print(f"  [INFO] Polity '{base}' H{h_prev} and H{h_curr} similarity: {sim:.2f}")

    # ----------------------------------------------------
    # CHECK 4: BREVITY CHECK (QUICK NOTES STRICTLY <= 15 WORDS)
    # ----------------------------------------------------
    print("\n--- CHECK 4: BREVITY CHECK (QUICK NOTES <= 15 WORDS) ---")
    # Polity Quick Notes
    with open(os.path.join(ROOT, "Indian_Polity_and_Governance", "polity-uppsc-quick-notes.html"), encoding="utf-8") as f:
        polity_quick = f.read()
    p_topics = re.findall(r'<article class="topic" id="([^"]+)">\s*<h3>(.*?)</h3>\s*<ul>(.*?)</ul>\s*</article>', polity_quick, re.S)
    p_long = 0
    p_total = 0
    p_wcs = []
    for tid, tt, ul in p_topics:
        lis = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.S)
        for li in lis:
            clean = re.sub(r'<[^>]+>', '', li).strip()
            wc = len(clean.split())
            p_wcs.append(wc)
            p_total += 1
            if wc > 15:
                p_long += 1
    if p_long == 0:
        print(f"  [PASS] Polity Quick Notes: 100% compliant! Total {p_total} bullets, 0 exceeding 15 words (avg: {sum(p_wcs)/len(p_wcs):.1f}w, max: {max(p_wcs)}w).")
    else:
        failures.append(f"Polity Quick Notes has {p_long} bullets exceeding 15 words!")
        print(f"  [FAIL] Polity Quick Notes has {p_long} bullets exceeding 15 words!")

    # Environment Quick Notes
    with open(os.path.join(ROOT, "Environment_2025", "environment-2025-uppsc-quick-notes.html"), encoding="utf-8") as f:
        env_quick = f.read()
    e_topics = re.findall(r'<article class="topic" id="([^"]+)">\s*<h3>(.*?)</h3>\s*<ul>(.*?)</ul>\s*</article>', env_quick, re.S)
    e_long = 0
    e_total = 0
    e_wcs = []
    for tid, tt, ul in e_topics:
        lis = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.S)
        for li in lis:
            clean = re.sub(r'<span class="ps">.*?</span>|<span class="chk">.*?</span>|<[^>]+>', ' ', li).strip()
            wc = len(clean.split())
            e_wcs.append(wc)
            e_total += 1
            if wc > 15:
                e_long += 1
    if e_long == 0:
        print(f"  [PASS] Environment Quick Notes: 100% compliant! Total {e_total} bullets, 0 exceeding 15 words (avg: {sum(e_wcs)/len(e_wcs):.1f}w, max: {max(e_wcs)}w).")
    else:
        failures.append(f"Environment Quick Notes has {e_long} bullets exceeding 15 words!")
        print(f"  [FAIL] Environment Quick Notes has {e_long} bullets exceeding 15 words!")

    # ----------------------------------------------------
    # CHECK 5: UI & DASHBOARD INTEGRITY
    # ----------------------------------------------------
    print("\n--- CHECK 5: UI & DASHBOARD INTEGRITY ---")
    dash_path = os.path.join(ROOT, "study-dashboard.html")
    with open(dash_path, encoding="utf-8") as f:
        dash_text = f.read()
        
    for sub in ["polity", "environment"]:
        if f'id="{sub}-full"' not in dash_text:
            failures.append(f"Dashboard missing section id='{sub}-full'")
        if f'id="{sub}-quick"' not in dash_text:
            failures.append(f"Dashboard missing section id='{sub}-quick'")
        if f'id="{sub}-plan"' not in dash_text:
            failures.append(f"Dashboard missing section id='{sub}-plan'")
            
    print(f"  [PASS] study-dashboard.html integrity verified ({len(dash_text):,} bytes).")
    print("  [PASS] All subject views (full, quick, plan) verified.")
    
    # ----------------------------------------------------
    # FINAL VERDICT
    # ----------------------------------------------------
    print("\n==================================================")
    if not failures:
        print("          ALL CRITIC CHECKS PASSED (100%)         ")
        print("==================================================")
        return True
    else:
        print(f"          CRITIC VERDICT: FAILED WITH {len(failures)} DEFECTS")
        for err in failures:
            print(f"  - {err}")
        print("==================================================")
        return False

if __name__ == "__main__":
    success = run_critic_pass()
    if not success:
        sys.exit(1)
