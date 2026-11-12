import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "chapters_1_21.json"), encoding="utf-8") as f:
    ch1_21 = json.load(f)

with open(os.path.join(base_dir, "chapters_22_42.json"), encoding="utf-8") as f:
    ch22_42 = json.load(f)

all_chapters = ch1_21 + ch22_42

# Ensure topic mapping for questions
with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
    qs = json.load(f)

# Build valid anchors set
valid_anchors = {}
for ch in all_chapters:
    ch_id = f"c{ch['num']}"
    valid_anchors[ch_id] = [t["id"] for t in ch["topics"]]

# Update question anchors
for qid, q in qs.items():
    ch_id = q["ch"]
    topics = valid_anchors.get(ch_id, [f"{ch_id}-t1"])
    # If anchor not valid or default, keep within range
    if "h" not in q or q["h"] not in topics:
        q["h"] = topics[0]

with open(os.path.join(base_dir, "structured_all_chapters.json"), "w", encoding="utf-8") as f:
    json.dump(all_chapters, f, indent=2, ensure_ascii=False)

with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), "w", encoding="utf-8") as f:
    json.dump(qs, f, indent=2, ensure_ascii=False)

print(f"Merged all {len(all_chapters)} chapters into structured_all_chapters.json ({os.path.getsize(os.path.join(base_dir, 'structured_all_chapters.json')):,} bytes)")
