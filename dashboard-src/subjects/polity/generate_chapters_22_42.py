import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
from polity_builder_lib import generate_clean_chapter

def main():
    print("Generating Chapters 22 to 42 (Clean, Deduplicated, Compressed)...")
    chapters = []
    for c_num in range(22, 43):
        ch = generate_clean_chapter(c_num)
        chapters.append(ch)
        pts_count = sum(len(t['points']) for t in ch['topics'])
        print(f"  Ch {c_num:02d}: {ch['title'][:35]:<35} | {len(ch['topics'])} topics | {pts_count} clean pts")
        
    out_file = os.path.join(HERE, "chapters_22_42.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {out_file} ({os.path.getsize(out_file):,} bytes)")

if __name__ == "__main__":
    main()
