"""One-time copy of the page templates from the old History pipeline (since retired; it is in git
history). The copies already live in this folder, so a re-run finds no source and changes nothing."""
import shutil
import os

src_dir = os.path.join("dashboard-src", "subjects", "history")
dst_dir = os.path.join("dashboard-src", "subjects", "geography")

templates = [
    "template_full_style.css",
    "template_full_js.html",
    "template_quick_style.css",
    "template_quick_js.html",
    "template_72h_style.css",
    "template_72h_js.html",
]

for t in templates:
    src = os.path.join(src_dir, t)
    dst = os.path.join(dst_dir, t)
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"Copied {t} ({os.path.getsize(dst):,} bytes)")
    elif os.path.exists(dst):
        print(f"Kept existing {t}")

print("Templates ready in geography directory.")
