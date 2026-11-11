with open("Indian_Polity_2026/polity-uppsc-full-notes.html", encoding="utf-8") as f:
    text = f.read()

pos = text.find('id="c1"')
print("Snippet around c1:")
print(text[pos-100:pos+1500])
