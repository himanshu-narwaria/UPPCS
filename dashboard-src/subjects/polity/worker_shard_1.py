import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
from polity_builder_lib import generate_clean_chapter

def run_shard_1():
    print("=== RUNNING POLITY WORKER SHARD 1: CHAPTERS 1 TO 14 ===")
    chapters = []
    total_pts = 0
    pts_out_of_bounds = 0
    cross_topic_dups = 0
    
    for c_num in range(1, 15):
        ch = generate_clean_chapter(c_num)
        chapters.append(ch)
        
        # Check uniqueness across topics of this chapter
        seen_pts = set()
        ch_pts_count = 0
        for t in ch["topics"]:
            for p in t["points"]:
                ch_pts_count += 1
                total_pts += 1
                wc = len(p["html"].split())
                if wc < 8 or wc > 15:
                    pts_out_of_bounds += 1
                    print(f"  WARNING: Ch {c_num} {t['id']} bullet out of bounds ({wc}w): {p['html']}")
                norm = p["html"].lower()
                if norm in seen_pts:
                    cross_topic_dups += 1
                    print(f"  DUPLICATE in Ch {c_num}: {p['html']}")
                seen_pts.add(norm)
                
        print(f"  Ch {c_num:02d}: {ch['title'][:35]:<35} | {len(ch['topics'])} topics | {ch_pts_count} clean pts")

    out_file = os.path.join(HERE, "chapters_1_14_clean.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)
        
    print(f"\nShard 1 Done: {len(chapters)} chapters, {total_pts} points.")
    print(f"Points out of bounds (8-15 words): {pts_out_of_bounds}")
    print(f"Cross-topic duplicates: {cross_topic_dups}")
    assert pts_out_of_bounds == 0, f"{pts_out_of_bounds} points out of bounds!"
    assert cross_topic_dups == 0, f"{cross_topic_dups} cross topic duplicates!"
    print(">>> SHARD 1 PASSED ALL ASSERTIONS! <<<")

if __name__ == "__main__":
    run_shard_1()
