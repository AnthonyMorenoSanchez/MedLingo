import re


def normalized(term):
    result = dict(term)
    for lang in ("en", "es"):
        value = re.sub(r"\s+", " ", result[lang]).strip().rstrip(".")
        result[lang] = value if value.isupper() else value[:1].lower() + value[1:]
    if not result["en"] or not result["es"] or len(result["en"]) > 120 or len(result["es"]) > 150:
        return None
    if result["en"] == result["es"] and result.get("semantic_type") not in ("drug", "anatomy"):
        return None
    return result

def dedupe(terms):
    seen: dict = {}
    for term in terms:
        item = normalized(term)
        if item:
            key = (item["en"], item["es"])
            if key in seen:
                seen[key]["specialties"] = sorted(set(seen[key].get("specialties", []) + item.get("specialties", [])))
            else:
                seen[key] = item
    return [seen[k] for k in sorted(seen)]
