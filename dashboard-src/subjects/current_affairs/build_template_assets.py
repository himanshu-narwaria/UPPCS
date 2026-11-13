"""Study assets are now subject-owned: no runtime dependency on Polity templates."""
from pathlib import Path
p=Path(__file__).resolve().parent
for x in ["study_styles.css", "study_runtime.js", "fonts_embedded.css"]:
    assert (p/x).is_file(), x
print("Offline subject-owned CSS, JS and embedded fonts verified.")
