import re


class TemplateRenderError(ValueError):
    pass

def plural(word):
    irregular={"riñón":"riñones","región":"regiones","corazón":"corazones","pulmón":"pulmones","ganglión":"gangliones","raíz":"raíces","crisis":"crisis","tórax":"tórax","análisis":"análisis"}
    if word in irregular:
        return irregular[word]
    if word.endswith("z"):
        return word[:-1] + "ces"
    if word.endswith(("a", "e", "i", "o", "u", "á", "é", "ó")):
        return word + "s"
    return word + "es"

def render(pattern, slots, lang="es"):
    def replace(match):
        bits = match.group(1).split(":")
        op, key = (bits[0], bits[1]) if len(bits) > 1 else ("", bits[0])
        term = slots[key]
        word = term[lang]
        if not op:
            return word
        if op == "PL":
            return term.get("plural_es") or plural(word)
        gender = term.get("gender_es")
        if gender not in ("m", "f", "mf"):
            raise TemplateRenderError(f"Unknown gender for {word}")
        feminine = gender == "f"
        multi = term.get("number_es", "sg") == "pl"
        if op in ("DET", "INDEF"):
            if not multi and word in ("agua", "águila", "asma", "área", "hambre", "hacha"):
                feminine = False
            return ({(False,False): "el", (True,False): "la", (False,True): "los", (True,True): "las"} if op == "DET" else {(False,False): "un", (True,False): "una", (False,True): "unos", (True,True): "unas"})[(feminine,multi)]
        if op == "ADJ":
            adjective = bits[2]
            if feminine and adjective.endswith("o"):
                adjective = adjective[:-1] + "a"
            return plural(adjective) if multi else adjective
        raise TemplateRenderError(f"Unknown slot operation {op}")
    return re.sub(r"\{([^{}]+)\}", replace, pattern)

def expand_slots(template, groups, limit=100):
    """Select deterministic combinations from declared term and fixed-option slots."""
    choices = {}
    for key, rule in template['slots'].items():
        if rule.get('type') == 'fixed':
            choices[key] = rule.get('options', [])
        else:
            specialty = rule.get('filter', {}).get('specialty', template['specialty'])
            semantic = rule.get('type', 'any')
            choices[key] = [t for t in groups.get(specialty, [])
                            if t.get('pos') != 'phrase' and (semantic == 'any' or t.get('semantic_type') == semantic)]
        if not choices[key]:
            return
    if not choices:
        yield {}
        return
    lengths = [len(v) for v in choices.values()]
    count = min(limit, max(lengths))
    for i in range(count):
        yield {key: values[i % len(values)] for key, values in choices.items()}
