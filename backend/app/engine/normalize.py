import re
import unicodedata

from rapidfuzz.fuzz import ratio


def normalize(value: str, article_required=False, accents=False) -> str:
    value = re.sub(r"\s+", " ", value.lower().strip().strip("¿¡?!.,;: "))
    if not article_required:
        value = re.sub(r"^(el|la|los|las|un|una)\s+", "", value)
    if accents:
        value = "".join(c for c in unicodedata.normalize("NFD", value) if not unicodedata.combining(c))
    return value

def check(given: str, answers: list[str], article_required=False) -> tuple[str, str]:
    a = normalize(given, article_required)
    if any(a == normalize(b, article_required) for b in answers):
        return "correct", "exact"
    folded = normalize(given, article_required, True)
    if any(folded == normalize(b, article_required, True) for b in answers):
        return "correct", "accents"
    if any(ratio(folded, normalize(b, article_required, True)) >= 92 for b in answers):
        return "wrong", "near_miss"
    return "wrong", "incorrect"
