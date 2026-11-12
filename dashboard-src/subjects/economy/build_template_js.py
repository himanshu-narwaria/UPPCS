import os

base_dir = os.path.join("dashboard-src", "subjects", "economy")
polity_js_path = os.path.join("dashboard-src", "subjects", "polity", "template_quick_js.html")

with open(polity_js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Replace polity-specific strings with economy
eco_js = js.replace('Indian Polity Quick Revision', 'Economy Quick Revision')
eco_js = eco_js.replace('polgovup-imp', 'ecoup-imp')
eco_js = eco_js.replace('polgov-theme', 'eco-theme')

out_path = os.path.join(base_dir, "template_quick_js.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(eco_js)

print(f"Created {out_path} ({len(eco_js):,} chars)")
