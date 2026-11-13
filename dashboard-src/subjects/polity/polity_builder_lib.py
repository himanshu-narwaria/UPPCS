"""Build the readable chapter layer without arbitrary word truncation."""
import html
from build_polity_data import CHAPTER_SPECS
from learning_guides import GUIDES, MEMORY_HOOKS


def generate_clean_chapter(ch_num):
    _, title, start, _ = CHAPTER_SPECS[ch_num - 1]
    end = CHAPTER_SPECS[ch_num][2] if ch_num < len(CHAPTER_SPECS) else 530
    gist, points, comparison, confusion, recalls = GUIDES[ch_num]
    return {"num": ch_num, "title": title, "part": "Indian Polity and Governance",
            "gist": gist, "focus": [], "pages": [start, end],
            "topics": [{"id": f"c{ch_num}-t1", "title": "Build the idea",
                        "pg": f"PDF pp. {start}-{end}",
                        "points": [{"html": html.escape(p), "keep": True,
                                    "asked": False, "hot": False} for p in points]}],
            "comparison": comparison, "confusion": confusion,
            "recall": recalls + [("Spot the trap: what distinction must you keep clear in this chapter?", confusion)],
            "memory_hook": MEMORY_HOOKS.get(ch_num)}
