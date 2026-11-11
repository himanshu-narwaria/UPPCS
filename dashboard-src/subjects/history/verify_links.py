import re, os, sys
from urllib.parse import unquote

def verify_file_internal_anchors(path):
    print(f"\nVerifying anchors in {path}...")
    with open(path, encoding="utf-8") as f:
        content = f.read()
        
    # Strip <script>...</script> so we only check real HTML hrefs
    html_only = re.sub(r'<script.*?</script>', '', content, flags=re.S)
    
    ids = set(re.findall(r'id=["\']([^"\']+)["\']', html_only))
    print(f"  Found {len(ids)} unique HTML IDs.")
    
    hrefs = re.findall(r'href=["\']#([^"\']+)["\']', html_only)
    broken = [h for h in hrefs if h and h not in ids]
            
    if broken:
        print(f"  FAILED: {len(broken)} broken HTML anchors found: {list(set(broken))[:15]}")
    else:
        print(f"  SUCCESS: All {len(hrefs)} internal anchors resolve perfectly!")
    return len(broken) == 0

def verify_dashboard_links():
    print("\nVerifying study-dashboard.html links to Indian History...")
    with open("study-dashboard.html", encoding="utf-8") as f:
        content = f.read()
    
    links = re.findall(r'href=["\'](Indian_History_Part_2/[^"\'#]+)(?:#[^"\']*)?["\']', content)
    unique_links = set(links)
    print(f"  Found {len(unique_links)} unique file links to Indian_History_Part_2.")
    broken = []
    for link in unique_links:
        unquoted = unquote(link)
        if not os.path.exists(unquoted):
            broken.append(unquoted)
            
    if broken:
        print(f"  FAILED: Broken links: {broken}")
    else:
        print(f"  SUCCESS: All links resolve to existing files: {unique_links}")
    return len(broken) == 0

if __name__ == "__main__":
    ok1 = verify_file_internal_anchors("Indian_History_Part_2/history-uppsc-full-notes.html")
    ok2 = verify_file_internal_anchors("Indian_History_Part_2/history-uppsc-quick-notes.html")
    ok3 = verify_file_internal_anchors("Indian_History_Part_2/history-in-72h.html")
    ok4 = verify_dashboard_links()
    
    if ok1 and ok2 and ok3 and ok4:
        print("\nALL LINK VERIFICATIONS PASSED 100%!")
    else:
        sys.exit(1)
