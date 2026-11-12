import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "chapters_1_14_clean.json"), encoding="utf-8") as f:
    s1 = json.load(f)

with open(os.path.join(HERE, "chapters_15_28_clean.json"), encoding="utf-8") as f:
    s2 = json.load(f)

with open(os.path.join(HERE, "chapters_29_42_clean.json"), encoding="utf-8") as f:
    s3 = json.load(f)

all_42 = s1 + s2 + s3
assert len(all_42) == 42, f"Expected 42 chapters, got {len(all_42)}"

ch_1_21 = all_42[:21]
ch_22_42 = all_42[21:]

with open(os.path.join(HERE, "chapters_1_21.json"), "w", encoding="utf-8") as f:
    json.dump(ch_1_21, f, indent=2, ensure_ascii=False)

with open(os.path.join(HERE, "chapters_22_42.json"), "w", encoding="utf-8") as f:
    json.dump(ch_22_42, f, indent=2, ensure_ascii=False)

with open(os.path.join(HERE, "structured_all_chapters.json"), "w", encoding="utf-8") as f:
    json.dump(all_42, f, indent=2, ensure_ascii=False)

print(f"Merged all 42 chapters: {len(all_42)} chapters saved.")
print(f"chapters_1_21.json: {len(ch_1_21)} chapters")
print(f"chapters_22_42.json: {len(ch_22_42)} chapters")
print(f"structured_all_chapters.json: {len(all_42)} chapters")
