"""The three chapterwise solved-paper books and where their pages go."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]          # the site folder

BOOKS = {
    "polity": {
        "name": "Indian Polity", "hindi": "भारतीय राजव्यवस्था", "letter": "D",
        "pdf": ROOT / "Indian_Polity_and_Governance" / "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf",
        "out": ROOT / "Indian_Polity_and_Governance",
        "files": ("polity-uppsc-full-notes.html", "polity-uppsc-quick-notes.html", "polity-in-72h.html"),
        "plan_key": "polgov72-v2-done", "prefix": "pol",
        "shift": 0, "pages": 530, "writers": 6,
        # Questions whose print the text layer cannot carry, keyed "chapter-question". Each was
        # read from the page image. Options are replaced; "mid" replaces the statements.
        "corrections": {
            # p222: options printed as stacked fractions (1 over 3 ...), read as stray digits
            "22-061": {"mid": [], "options": {"a": "1/3 of valid votes", "b": "1/4 of valid votes",
                                              "c": "1/5 valid votes", "d": "None of the above"}},
        },
    },
    "history": {
        "name": "Indian History", "hindi": "भारतीय इतिहास", "letter": "B",
        "pdf": ROOT / "Indian_History_Part_2" / "Preview_Indian_History_Part_2_2026_26116_C_E_Book_Merged_1.pdf",
        "out": ROOT / "Indian_History_Part_2",
        "files": ("history-uppsc-full-notes.html", "history-uppsc-quick-notes.html", "history-in-72h.html"),
        "plan_key": "his72-v2-done", "prefix": "his",
        "shift": 0, "pages": 760, "writers": 9,
    },
    "economy": {
        "name": "Economy", "hindi": "अर्थव्यवस्था", "letter": "E",
        "pdf": ROOT / "Economy 2024" / "Ghatnachakra Economy 2024_261031_191426.pdf",
        "out": ROOT / "Economy 2024",
        "files": ("economy-uppsc-full-notes.html", "economy-uppsc-quick-notes.html", "economy-in-72h.html"),
        "plan_key": "eco72-v2-done", "prefix": "eco",
        # this PDF stores every character 29 code points low ("7KH" = "The")
        "shift": 29, "pages": 578, "writers": 7,
    },
    "geography": {
        "name": "General Geography", "hindi": "सामान्य भूगोल",
        "pdf": ROOT / "General_Geography_Part_3" / "Preview_General_Geography_Part_3_2026_26117_C_E_Book_combined.pdf",
        "out": ROOT / "General_Geography_Part_3",
        "files": ("geography-uppsc-full-notes.html", "geography-uppsc-quick-notes.html", "geography-in-72h.html"),
        "plan_key": "geo72-v2-done", "prefix": "geo",
        # questions are numbered afresh in every sub-topic ("i. Area"): see name_chapters
        "subtopics": True,
        "shift": 0, "pages": 708, "writers": 8,
    },
    "science": {
        "name": "General Science", "hindi": "सामान्य विज्ञान",
        "pdf": ROOT / "General_Science_Part_7" / "Preview_General_Science_Part_7_2026_26121_C_E_Book_combined_1.pdf",
        "out": ROOT / "General_Science_Part_7",
        "files": ("science-uppsc-full-notes.html", "science-uppsc-quick-notes.html", "science-in-72h.html"),
        "plan_key": "sci72-v2-done", "prefix": "sci",
        # questions are numbered afresh in every sub-topic ("i. Area"): see name_chapters
        "subtopics": True,
        "shift": 0, "pages": 760, "writers": 8,
    },
}


def book_dir(key):
    d = HERE / key
    d.mkdir(exist_ok=True)
    return d
