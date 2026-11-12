import os

base_dir = os.path.join("dashboard-src", "subjects", "economy")
polity_css_path = os.path.join("dashboard-src", "subjects", "polity", "template_quick_style.css")
fonts_path = os.path.join(base_dir, "fonts_embedded.css")

with open(fonts_path, "r", encoding="utf-8") as f:
    fonts_css = f.read()

with open(polity_css_path, "r", encoding="utf-8") as f:
    polity_css = f.read()

# Update polity CSS to use Atkinson and Lexend
economy_css = polity_css.replace(
    'font:16.5px/1.55 system-ui,-apple-system,"Segoe UI","Nirmala UI",Roboto,Arial,sans-serif',
    'font:16.5px/1.55 "Atkinson Hyperlegible Next","Segoe UI",system-ui,Arial,"Nirmala UI",sans-serif'
)

economy_css = economy_css.replace(
    'h1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}',
    'h1,h2,.brand{font-family:"Lexend","Segoe UI",system-ui,sans-serif}\nh1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}'
)

# Prepend the offline @font-face blocks
full_css = fonts_css + "\n" + economy_css

out_path = os.path.join(base_dir, "template_quick_style.css")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(full_css)

print(f"Created {out_path} ({len(full_css):,} chars)")
