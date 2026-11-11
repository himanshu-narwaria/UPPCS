import json, re
from collections import Counter

with open("dashboard-src/subjects/history/raw_pages.json", encoding="utf-8") as f:
    pages = json.load(f)

# Exam patterns in Ghatna Chakra:
# Common UPPSC patterns:
# U.P.P.C.S. (Pre) 2018
# U.P. P.C.S. (Pre) 2010
# U.P.P.C.S. (Mains) 2006
# U.P.P.C.S. (Spl) (Pre) 2008
# U.P. Lower Sub. (Pre) 2004
# U.P. Lower Spl. (Pre) 2008
# U.P. Lower (Pre) 2002
# U.P. Lower Sub. (Mains) 2013
# U.P. R.O./A.R.O. (Pre) 2017
# U.P.R.O./A.R.O. (Mains) 2014
# U.P. U.D.A./L.D.A. (Pre) 2006
# U.P. UDA/LDA (Mains) 2010
# U.P.P.S.C. (GIC) 2010
# U.P. GDC 2021
# U.P. B.E.O. (Pre) 2019
# U.P.P.C.S. (RI) 2014

# Non-UPPSC patterns to NEVER count as UPPSC:
# I.A.S., U.P.S.C., B.P.S.C. (Bihar), M.P.P.C.S. / M.P.S.C. (MP), R.A.S. / R.T.S. (Rajasthan),
# J.P.S.C. (Jharkhand), Chhattisgarh / C.G.P.C.S., Uttarakhand / U.K.P.C.S. / U.K. UDA/LDA.
# Note: Uttarakhand is NOT UPPSC! (U.K. or Uttarakhand).

def is_uppsc_exam(line):
    # Must NOT be Uttarakhand or UK
    if re.search(r'\b(Uttarakhand|U\.?K\.?)\b', line, re.I):
        return False
    # Must match UPPSC patterns
    if re.search(r'\b(U\.?P\.?P?\.?C\.?S|U\.?P\.?\s*P\.?S\.?C|U\.?P\.?\s*Lower|U\.?P\.?\s*R\.?O|U\.?P\.?\s*A\.?R\.?O|U\.?P\.?\s*U\.?D\.?A|U\.?P\.?\s*L\.?D\.?A|U\.?P\.?\s*G\.?I\.?C|U\.?P\.?\s*G\.?D\.?C|U\.?P\.?\s*B\.?E\.?O|U\.?P\.?\s*R\.?I)\b', line, re.I):
        return True
    return False

# Scan all pages for exam lines
detected = []
rejected = []
for p in pages:
    for l in p["text"].split("\n"):
        line = l.strip()
        # Look for lines with a year e.g. 1990-2025 and an exam name
        if re.search(r'\b(19\d\d|20[0-2]\d)\b', line) and re.search(r'\((Pre|Mains|Spl|Re-exam)\)|\b(PCS|IAS|BPSC|MPPCS|RAS|RTS|JPSC|CGPCS|RO|ARO|GIC|BEO|RI)\b', line, re.I):
            if is_uppsc_exam(line):
                detected.append((p["pdf_page"], line))
            else:
                rejected.append((p["pdf_page"], line))

print(f"Total UPPSC exam matches: {len(detected)}")
print(f"Total non-UPPSC exam matches: {len(rejected)}")

print("\nSample 20 UPPSC exam matches:")
for p, l in detected[:20]:
    print(f"  p.{p}: {l}")

print("\nSample 15 non-UPPSC exam matches (verifying no UPPSC was wrongly rejected):")
for p, l in rejected[:15]:
    print(f"  p.{p}: {l}")
