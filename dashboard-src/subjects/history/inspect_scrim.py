with open("Indian_Polity_2026/polity-in-72h.html", encoding="utf-8") as f:
    text = f.read()

idx = text.find('id="scrim"')
print("SCRIM CONTEXT:")
print(text[idx-100:idx+150])
