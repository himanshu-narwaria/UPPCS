import json
import re

with open("Indian_Polity_2026/polity-uppsc-full-notes.html", "r", encoding="utf-8") as f:
    old_html = f.read()

with open("dashboard-src/subjects/polity/parsed_chapter_stats.json", "r", encoding="utf-8") as f:
    new_stats = json.load(f)

old_counts = {}
for m in re.finditer(r'<a href="#c(\d+)"[^>]*>.*?<span class="q">(\d+)\s+UPPSC PYQs</span></a>', old_html):
    old_counts[int(m.group(1))] = int(m.group(2))

print(f"{'Ch':>3} {'Title':<45} {'Old':>5} {'New':>5} {'Diff':>5}")
print("-" * 68)
total_old = sum(old_counts.values())
total_new = sum(new_stats.values())

from build_polity_data import CHAPTER_SPECS

for ch_num, title, _, _ in CHAPTER_SPECS:
    old_c = old_counts.get(ch_num, 0)
    new_c = new_stats.get(str(ch_num), new_stats.get(ch_num, 0))
    diff = new_c - old_c
    diff_str = f"+{diff}" if diff > 0 else str(diff)
    print(f"{ch_num:3d} {title[:44]:<45} {old_c:5d} {new_c:5d} {diff_str:>5}")

print("-" * 68)
print(f"Total UPPSC questions: Old = {total_old}, New = {total_new} (Diff: +{total_new - total_old})")
