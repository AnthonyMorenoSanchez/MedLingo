from pathlib import Path

import yaml

OVERRIDES = yaml.safe_load((Path(__file__).parent / "curated/gender_overrides.yaml").read_text())
def infer(word):
    if word in OVERRIDES:
        return OVERRIDES[word]
    first = word.split()[0].lower()
    if first in OVERRIDES:
        return OVERRIDES[first]
    if first.endswith("s") and len(first)>3:
        singular = first[:-1]
        if singular in OVERRIDES:
            return OVERRIDES[singular]
        if singular.endswith(("a","o")):
            return "f" if singular.endswith("a") else "m"
    if first.endswith(("ción", "sión", "dad", "tad", "tud", "umbre", "itis", "a")):
        return "f"
    if first.endswith(("o", "or", "aje", "oma")):
        return "m"
    return None
