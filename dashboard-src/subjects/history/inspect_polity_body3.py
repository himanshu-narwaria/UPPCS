with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

idx = text.find("<body>")
idx_home = text.find('id="home"')
print(text[idx:idx_home])
