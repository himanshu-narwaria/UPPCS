import re

def inspect_all():
    with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
        s_72 = f.read()
    print("=== POLITY 72H PLAN ===")
    print("Length:", len(s_72))
    m_nav = re.search(r'<nav class="side" id="side"[^>]*>(.*?)</nav>', s_72, re.S)
    if m_nav:
        print("Nav snippet:\n", m_nav.group(0)[:600])
    m_h1 = re.search(r'<section class="view[^"]*" id="h1"[^>]*>.*?</section>', s_72, re.S)
    if m_h1:
        print("\nh1 view snippet:\n", m_h1.group(0)[:800])
        print("...\n", m_h1.group(0)[-400:])

    with open("Environment_2025/environment-2025-uppsc-quick-notes.html", encoding="utf-8") as f:
        s_q = f.read()
    print("\n=== ENVIRONMENT QUICK NOTES ===")
    print("Length:", len(s_q))
    m_home = re.search(r'<section class="view" id="home".*?</section>', s_q, re.S)
    if m_home:
        print("Quick notes home snippet:\n", m_home.group(0)[:600])
    m_rep = re.search(r'<section class="view" id="repeated".*?</section>', s_q, re.S)
    if m_rep:
        print("\nQuick notes repeated snippet:\n", m_rep.group(0)[:600])
    m_c1 = re.search(r'<section class="view ch" id="c1".*?</section>', s_q, re.S)
    if m_c1:
        print("\nQuick notes c1 snippet:\n", m_c1.group(0)[:600])

if __name__ == "__main__":
    inspect_all()
