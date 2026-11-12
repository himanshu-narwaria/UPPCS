import json
import re
import os

def build_repeated_and_latest():
    base_dir = os.path.join("dashboard-src", "subjects", "polity")
    with open(os.path.join(base_dir, "parsed_uppsc_questions.json"), encoding="utf-8") as f:
        qs = json.load(f)

    # 1. Repeated facts (n >= 2)
    repeats = []
    seen_facts = set()

    for qid, q in qs.items():
        if q["n"] >= 2:
            fact = q.get("f", "").strip()
            if not fact or "See the explanation" in fact or len(fact) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                fact = f"{q['s']} → <b>{ans_txt}</b>"
            else:
                fact = re.sub(r'D[–-]\d+.*', '', fact)
                fact = re.sub(r'\s+', ' ', fact).strip()

            norm_fact = re.sub(r'[^a-zA-Z0-9]', '', fact.lower())[:50]
            if norm_fact in seen_facts:
                continue
            seen_facts.add(norm_fact)

            ch_num = int(q["ch"][1:])
            repeats.append({
                "fact": fact,
                "count": q["n"],
                "papers": q["e"],
                "anchor": f"c{ch_num}-t1",
                "ch": ch_num
            })

    # Sort by count descending, then chapter number
    repeats.sort(key=lambda r: (-r["count"], r["ch"]))

    with open(os.path.join(base_dir, "repeated_facts.json"), "w", encoding="utf-8") as f:
        json.dump(repeats, f, indent=2, ensure_ascii=False)

    print(f"Total repeated facts: {len(repeats)}")
    print("Top 5 repeated facts:")
    for r in repeats[:5]:
        print(f"  ×{r['count']} (Ch {r['ch']}): {r['fact'][:80]}... [{r['papers']}]")

    # 2. Latest facts (2021-2025)
    latest_by_year = {}
    for qid, q in qs.items():
        y = q["y"]
        if y >= 2021:
            if y not in latest_by_year:
                latest_by_year[y] = []
            
            fact = q.get("f", "").strip()
            if not fact or "See the explanation" in fact or len(fact) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                fact = f"{q['s']} → <b>{ans_txt}</b>"
            else:
                fact = re.sub(r'\s+', ' ', fact).strip()

            ch_num = int(q["ch"][1:])
            latest_by_year[y].append({
                "fact": fact[:140] + ("..." if len(fact) > 140 else ""),
                "exam": q["e"],
                "count": q["n"],
                "anchor": f"c{ch_num}-t1",
                "ch": ch_num
            })

    with open(os.path.join(base_dir, "latest_facts.json"), "w", encoding="utf-8") as f:
        json.dump(latest_by_year, f, indent=2, ensure_ascii=False)

    print("\nLatest questions by year:")
    for yr in sorted(latest_by_year.keys(), reverse=True):
        print(f"  {yr}: {len(latest_by_year[yr])} items")

if __name__ == "__main__":
    build_repeated_and_latest()
