"""Chapter specification and real exam-label formatting for the source parser."""
import json
from pathlib import Path
import re

CHAPTER_SPECS = [
    (1, "The Constitutional Development of India", 7, r'The Constitutional Development\s+of India'),
    (2, "Constituent Assembly and Making of the Constitution", 17, r'Constituent Assembly and making\s+of the Constitution'),
    (3, "Important Committees of Constituent Assembly", 29, r'Important Committees of the\s+Constituent Assembly'),
    (4, "Sources of the Constitution", 31, r'Sources of the Constitution'),
    (5, "Parts of Indian Constitution", 37, r'Parts of the Indian Constitution'),
    (6, "Articles of the Constitution", 41, r'Articles of the Constitution\s*\n\*There were'),
    (7, "Schedules", 50, r'\nSchedules\s*\n'),
    (8, "The Preamble", 61, r'The Preamble\s*\*The Objectives'),
    (9, "The Governance System", 69, r'The Governance System'),
    (10, "National Symbols", 87, r'National Symbols'),
    (11, "States and Union Territories", 90, r'States and the Union Territories'),
    (12, "The Citizenship", 102, r'The Citizenship'),
    (13, "Fundamental Rights", 105, r'Fundamental Rights'),
    (14, "Directive Principles of State Policy", 136, r'Directive Principles of State Policy'),
    (15, "Fundamental Duties", 150, r'Fundamental Duties'),
    (16, "The President", 156, r'The President'),
    (17, "The Vice-President", 179, r'The Vice-President'),
    (18, "The Council of Ministers", 184, r'The Council of Ministers'),
    (19, "The Attorney General and the C.A.G.", 199, r'The Attorney-General and\s+the C\.A\.G\.|The Attorney-General and the C\.A\.G\.'),
    (20, "Order of Precedence", 210, r'Order of Precedence'),
    (21, "The Parliament (1)", 212, r'The Parliament \(1\)'),
    (22, "The Parliament (2)", 231, r'The Parliament \(2\)'),
    (23, "The Parliament (3)", 243, r'The Parliament \(3\)'),
    (24, "Parliamentary Committees", 269, r'Parliamentary Committees'),
    (25, "The Parliamentary Act", 277, r'Parliamentary Act'),
    (26, "The Supreme Court", 295, r'The Supreme Court'),
    (27, "The Governor", 320, r'The Governor'),
    (28, "The State Legislature", 331, r'The State Legislature'),
    (29, "The High Court", 347, r'The High Court'),
    (30, "The Centre-State Relations", 356, r'The Centre-State Relation'),
    (31, "Emergency Provisions", 367, r'Emergency Provisions'),
    (32, "The Finance Commission", 375, r'The Finance Commission'),
    (33, "The Planning Commission/NITI Aayog", 381, r'The Planning Commission\s*/\s*NITI AAYOG'),
    (34, "Lokpal and Important Commissions", 386, r'Lokpal and Important\s+Commissions'),
    (35, "Temporary, Transitional and Special Provisions", 408, r'Temporary, Transitional and\s+Special Provisions'),
    (36, "Election Commission", 410, r'Election Commission'),
    (37, "Political Parties", 424, r'Political Parties'),
    (38, "Constitutional Amendments", 436, r'Constitutional Amendment'),
    (39, "Official Language", 454, r'Official Language'),
    (40, "Panchayati Raj and Community Development", 459, r'Panchayati Raj and\s+Community Development'),
    (41, "Special Provision for Certain Classes", 498, r'Special Provisions Relating to\s+Certain Classes'),
    (42, "Miscellaneous", 504, r'Miscellaneous')
]

HERE = Path(__file__).resolve().parent


def load_pages():
    return json.loads((HERE / "raw_pages.json").read_text(encoding="utf-8"))


def extract_chapter_texts(pages):
    from source_model import chapter_texts
    return chapter_texts(pages)


def is_uppsc(line):
    from source_model import UP
    return bool(UP.search(line))


def format_uppsc_exam(line):
    year_match = re.search(r"\b(?:19|20)\d{2}\b", line)
    if not year_match:
        raise ValueError(f"Exam label has no source year: {line}")
    year = int(year_match.group(0))
    year_short = "'" + str(year)[-2:]
    compact = re.sub(r"[\s.]", "", line).upper()
    special = " (Spl)" if re.search(r"\b(?:Spl|Special)\b", line, re.I) else ""
    mains = " Mains" if re.search(r"Mains", line, re.I) else " Pre"
    if "GIC" in compact:
        exam = "GIC"
    elif "GDC" in compact:
        exam = "GDC"
    elif "BEO" in compact:
        exam = "BEO"
    elif re.search(r"\bRI\b", compact):
        exam = "RI"
    elif "RO" in compact or "ARO" in compact:
        exam = "RO/ARO" + mains
    elif "UDA" in compact or "LDA" in compact:
        exam = "UDA/LDA" + mains
    elif "LOWER" in compact:
        exam = "Lower Sub" + (" Mains" if mains == " Mains" else "")
    else:
        exam = "PCS" + mains
    return f"{exam}{special} {year_short}", year


if __name__ == "__main__":
    from source_model import build
    build()
