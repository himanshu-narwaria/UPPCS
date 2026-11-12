import re
import html

def make_telegraphic_bullet(stem, fact="", qualifier_hint="", is_repeat=False):
    """
    Produce an ultra-crisp bullet strictly between 8 and 15 words.
    Format: Concept/Article → Core Rule → Exception/Year/Key Fact
    Never leaves trailing arrows or broken punctuation.
    """
    stem = re.sub(r'<[^>]+>', '', stem)
    stem = html.unescape(stem).strip()
    fact = re.sub(r'<[^>]+>', '', fact)
    fact = html.unescape(fact).strip()
    
    # Strip question boilerplates
    stem = re.sub(r'^(?:Which of the following|Consider the following|Under which|Who among the following|By which|In which|With reference to|The provision for the|The provision for|Mention the correct|According to the|According to|Who was the|What is the|Who is the|How many|In the Indian Constitution|In Indian Polity|As per the Constitution)\s+', '', stem, flags=re.I)
    stem = re.sub(r'^(?:was|is|were|are|did|can be|has been|appointed|named|known as|stated that|related to|provided that)\s+', '', stem, flags=re.I)
    stem = re.sub(r'\?$', '', stem).strip()
    
    # Clean fact / answer
    fact = re.sub(r'^(?:is|was|are|were|the|an|a)\s+', '', fact, flags=re.I)
    fact = re.sub(r'\.$', '', fact).strip()
    
    if "see the explanation" in fact.lower() or len(fact) < 4:
        fact = "Enshrined in Constitutional Framework"
        
    # Extract Article if present
    art_m = re.search(r'\bArticle\s+(\d+[A-Z]?)\b', stem + " " + fact + " " + qualifier_hint, re.I)
    art_str = f"Art {art_m.group(1)}" if art_m else ""
    
    # Extract Amendment if present
    amd_m = re.search(r'\b(\d+(?:st|nd|rd|th)?)\s+(?:Constitutional\s+)?Amendment\b', stem + " " + fact + " " + qualifier_hint, re.I)
    amd_str = f"{amd_m.group(1)} Amd" if amd_m else ""
    
    # Extract Year if present
    yr_m = re.search(r'\b(1[789]\d\d|20\d\d)\b', fact + " " + stem + " " + qualifier_hint)
    yr_str = yr_m.group(1) if yr_m else ""
    
    # Condense stem
    stem_words = stem.split()
    if len(stem_words) > 5:
        stem = " ".join(stem_words[:5])
        
    fact_words = fact.split()
    if len(fact_words) > 5:
        fact = " ".join(fact_words[:5])
        
    qualifier = art_str or amd_str or (f"Year {yr_str}" if yr_str else qualifier_hint) or "Key Rule"
    
    cand = f"{stem} → {fact} → {qualifier}."
    cand = re.sub(r'\s*→\s*→', ' →', cand)
    cand = re.sub(r'\s*→\s*\.', '.', cand)
    
    w = cand.split()
    if len(w) > 15:
        # Trim while keeping structure
        trimmed = w[:14]
        # Remove trailing arrow if ends with arrow
        if trimmed[-1] == '→':
            trimmed = trimmed[:-1]
        cand = " ".join(trimmed).rstrip('.,;:→ ') + "."
    elif len(w) < 8:
        cand = f"{stem} → Core Provision: {fact} → Exam Trigger ({qualifier})."
        w = cand.split()
        if len(w) > 15:
            cand = " ".join(w[:14]).rstrip('.,;:→ ') + "."
        elif len(w) < 8:
            cand = f"Constitutional Framework: {stem} → {fact} → Key Principle ({qualifier})."
            cand = " ".join(cand.split()[:14]).rstrip('.,;:→ ') + "."
            
    # Final cleanup
    cand = re.sub(r'\s*→\s*\.', '.', cand)
    cand = re.sub(r'\s*→\s*$', '.', cand)
    final_w = cand.split()
    assert 8 <= len(final_w) <= 15, f"Word count {len(final_w)} out of bounds: {cand}"
    assert not cand.endswith('→.'), f"Dangling arrow: {cand}"
    return cand

def test_engine():
    samples = [
        ("Regulating Act of 1773 established Supreme Court at Calcutta", "Sir Elijah Impey appointed first Chief Justice", "1774"),
        ("Fundamental Duties added to Part IVA", "Recommended by Swaran Singh Committee", "42nd Amendment 1976"),
        ("Article 40 provides for organization of village panchayats", "State shall take steps to organize village panchayats", "Article 40"),
        ("President of India impeachment procedure", "Quasi-judicial procedure initiated in either House of Parliament", "Article 61"),
        ("Preamble declared part of the basic structure", "Kesavananda Bharati v State of Kerala", "1973"),
    ]
    for s, f, e in samples:
        b = make_telegraphic_bullet(s, f, e)
        print(f"[{len(b.split())}w] {b}")

if __name__ == "__main__":
    test_engine()
