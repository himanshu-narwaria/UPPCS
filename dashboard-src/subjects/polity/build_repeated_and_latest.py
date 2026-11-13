"""Build revision indexes from real UPPSC labels, retaining complete questions."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def item(qid, question):
    answer = "; ".join(question["o"][index] for index in question["k"])
    return {"fact": f'{question["s"]} → <b>{answer}</b>',
            "explanation": question["f"], "question_id": qid,
            "count": question["n"], "papers": question["e"],
            "exam": question["e"], "anchor": question["h"],
            "ch": int(question["ch"][1:]), "pages": question["pages"]}


def build_repeated_and_latest():
    questions = json.loads((HERE / "parsed_uppsc_questions.json").read_text(encoding="utf-8"))
    repeats, latest = [], {}
    for qid, question in questions.items():
        record = item(qid, question)
        if question["n"] >= 2:
            repeats.append(record)
        if question["y"] >= 2021:
            latest.setdefault(question["y"], []).append(record)
    repeats.sort(key=lambda value: (-value["count"], value["ch"], value["question_id"]))
    for filename, data in [("repeated_facts.json", repeats), ("latest_facts.json", latest)]:
        (HERE / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Built {len(repeats)} repeated UPPSC items and {sum(map(len, latest.values()))} recent items without text truncation.")


if __name__ == "__main__":
    build_repeated_and_latest()
