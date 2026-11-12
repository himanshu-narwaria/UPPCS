import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

def merge():
    with open(os.path.join(base_dir, "chapters_1_36.json"), encoding="utf-8") as f:
        ch_1_36 = json.load(f)
    with open(os.path.join(base_dir, "chapters_37_65.json"), encoding="utf-8") as f:
        ch_37_65 = json.load(f)
        
    all_chapters = ch_1_36 + ch_37_65
    print(f"Total merged chapters: {len(all_chapters)}")
    assert len(all_chapters) == 65, f"Expected 65 chapters, got {len(all_chapters)}"
    
    out_file = os.path.join(base_dir, "structured_all_chapters.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chapters, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {out_file} ({os.path.getsize(out_file):,} bytes)")

if __name__ == "__main__":
    merge()
