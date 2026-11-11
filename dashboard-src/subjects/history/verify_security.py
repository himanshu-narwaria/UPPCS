import re
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print("Auditing root:", ROOT)

files_to_check = [
    os.path.join(ROOT, "Indian_History_Part_2", "history-uppsc-full-notes.html"),
    os.path.join(ROOT, "Indian_History_Part_2", "history-uppsc-quick-notes.html"),
    os.path.join(ROOT, "Indian_History_Part_2", "history-in-72h.html"),
    os.path.join(ROOT, "study-dashboard.html"),
]

SCRIPT_RE = re.compile(r"<script(\s[^>]*)?>(.*?)</script>", re.S | re.I)
DATA_TYPES = re.compile(r'type\s*=\s*"application/(?:json|ld\+json)"', re.I)
EVENT_HANDLER_RE = re.compile(r'\son[a-z]+\s*=\s*[\'"][^\'"]*[\'"]', re.I)
JS_LINK_RE = re.compile(r'href\s*=\s*[\'"]\s*javascript:', re.I)

total_errors = 0

for file_path in files_to_check:
    rel_path = os.path.relpath(file_path, ROOT)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n--- Checking security on: {rel_path} ---")
    
    # 1. External scripts
    for attrs, body in SCRIPT_RE.findall(content):
        attrs = attrs or ""
        if DATA_TYPES.search(attrs):
            continue
        if re.search(r'\ssrc\s*=', attrs, re.I):
            print(f"ERROR: External script found: {attrs.strip()}")
            total_errors += 1
            
    # Remove script tags before checking for inline event handlers
    content_no_scripts = SCRIPT_RE.sub("", content)
    
    # 2. Inline event handlers
    event_handlers = EVENT_HANDLER_RE.findall(content_no_scripts)
    if event_handlers:
        print(f"ERROR: Found {len(event_handlers)} inline event handlers: {event_handlers[:5]}")
        total_errors += len(event_handlers)
    else:
        print("Inline event handlers: 0 (PASSED)")
        
    # 3. Javascript links
    js_links = JS_LINK_RE.findall(content)
    if js_links:
        print(f"ERROR: Found {len(js_links)} javascript: links")
        total_errors += len(js_links)
    else:
        print("javascript: links: 0 (PASSED)")

print(f"\nTotal security errors: {total_errors}")
if total_errors == 0:
    print("ALL SECURITY AND CSP CHECKS PASSED WITH 0 ERRORS!")
