import re

def extract_polity_core():
    with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
        s = f.read()
        
    # Remove sitenav injected blocks: <!--sx:start-->...<!--sx:end--> and <style id="sx-style">...</style> and sx scripts
    s_clean = re.sub(r'<!--sx:start-->.*?<!--sx:end-->', '', s, flags=re.S)
    s_clean = re.sub(r'<style id="sx-style">.*?</style>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-data".*?</script>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-script".*?</script>', '', s_clean, flags=re.S)
    
    # Extract style block (contains @font-face and all CSS)
    m_style = re.search(r'<style>(.*?)</style>', s_clean, re.S)
    style_content = m_style.group(1) if m_style else ""
    
    # Extract client JS after pqd
    m_pqd = re.search(r'<script id="pqd"[^>]*>.*?</script>(.*?)</body>', s_clean, re.S)
    js_after_pqd = m_pqd.group(1).strip() if m_pqd else ""
    
    with open("dashboard-src/subjects/history/template_full_style.css", "w", encoding="utf-8") as f:
        f.write(style_content)
    with open("dashboard-src/subjects/history/template_full_js.html", "w", encoding="utf-8") as f:
        f.write(js_after_pqd)
    print(f"Extracted full notes style ({len(style_content)} chars) and JS ({len(js_after_pqd)} chars)")

def extract_72h_core():
    with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
        s = f.read()
    s_clean = re.sub(r'<!--sx:start-->.*?<!--sx:end-->', '', s, flags=re.S)
    s_clean = re.sub(r'<style id="sx-style">.*?</style>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-data".*?</script>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-script".*?</script>', '', s_clean, flags=re.S)
    
    m_style = re.search(r'<style>(.*?)</style>', s_clean, re.S)
    style_content = m_style.group(1) if m_style else ""
    
    # Extract JS
    m_js = re.findall(r'<script(?![^>]*id="pqd")[^>]*>(.*?)</script>', s_clean, re.S)
    all_js = "\n".join(f"<script>{j}</script>" for j in m_js if 'sx-' not in j)
    
    with open("dashboard-src/subjects/history/template_72h_style.css", "w", encoding="utf-8") as f:
        f.write(style_content)
    with open("dashboard-src/subjects/history/template_72h_js.html", "w", encoding="utf-8") as f:
        f.write(all_js)
    print(f"Extracted 72h style ({len(style_content)} chars) and JS ({len(all_js)} chars)")

def extract_quick_core():
    with open("Environment_2025/environment-2025-uppsc-quick-notes.html", encoding="utf-8") as f:
        s = f.read()
    s_clean = re.sub(r'<!--sx:start-->.*?<!--sx:end-->', '', s, flags=re.S)
    s_clean = re.sub(r'<style id="sx-style">.*?</style>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-data".*?</script>', '', s_clean, flags=re.S)
    s_clean = re.sub(r'<script id="sx-script".*?</script>', '', s_clean, flags=re.S)
    
    m_style = re.search(r'<style>(.*?)</style>', s_clean, re.S)
    style_content = m_style.group(1) if m_style else ""
    
    m_js = re.findall(r'<script(?![^>]*id="pqd")[^>]*>(.*?)</script>', s_clean, re.S)
    all_js = "\n".join(f"<script>{j}</script>" for j in m_js if 'sx-' not in j)
    
    with open("dashboard-src/subjects/history/template_quick_style.css", "w", encoding="utf-8") as f:
        f.write(style_content)
    with open("dashboard-src/subjects/history/template_quick_js.html", "w", encoding="utf-8") as f:
        f.write(all_js)
    print(f"Extracted quick notes style ({len(style_content)} chars) and JS ({len(all_js)} chars)")

if __name__ == "__main__":
    extract_polity_core()
    extract_72h_core()
    extract_quick_core()
