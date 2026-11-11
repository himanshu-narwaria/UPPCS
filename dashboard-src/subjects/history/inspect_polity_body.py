with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

# Find everything between </style></head><body> and <section class="view" id="home">
import re
m = re.search(r'</style></head><body>(.*?)<section class="view" id="home">', text, re.S)
if m:
    print("BODY TO HOME:")
    print(m.group(1))

# Check home section full content
m_home = re.search(r'<section class="view" id="home">(.*?)</section>', text, re.S)
if m_home:
    print("\nHOME CONTENT:")
    print(m_home.group(0))
