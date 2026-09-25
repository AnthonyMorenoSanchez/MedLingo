RULES = {
"urology": ("C12", "E04.950"), "hematology": ("C15", "D17", "E01.370.225", "A15"),
"cardiology": ("C14", "A07", "E04.100"), "pulmonology": ("C08", "A04"),
"gastroenterology": ("C06", "A03"), "neurology": ("C10", "A08"),
"obgyn": ("C13", "A16"), "orthopedics": ("C05", "A02"),
"psychiatry": ("F03", "F01"), "pediatrics": ("C16",), "emergency": ("C26",), "anatomy": ("A",)}
WORDS = {
"urology": ["urin", "kidney", "renal", "prostat", "bladder", "ureth", "ureter", "testic", "penis", "scrot"],
"hematology": ["blood", "anemia", "anaemia", "hemato", "haemato", "leuk", "lymphom", "platelet", "coagula", "hemoph", "haemoph", "thalass", "thrombo"],
"cardiology": ["cardi", "heart", "coronary", "aortic", "arter", "arrhyth", "hypertens", "vascular", "vein"],
"pulmonology": ["pulmon", "lung", "respirat", "bronch", "asthma", "pneum", "pleur", "trache", "cough"],
"gastroenterology": ["gastro", "intestin", "gastric", "bowel", "stomach", "hepati", "liver", "pancrea", "esoph", "oesoph", "digest", "colon", "rectal", "biliar", "gallbladder"],
"neurology": ["neuro", "brain", "cerebr", "spinal", "epilep", "seizure", "nerve", "encephal", "parkinson", "alzheimer", "migraine"],
"obgyn": ["pregnan", "obstet", "gynec", "gynaec", "uter", "ovari", "vagin", "placent", "menstr", "breast", "cervix", "fetal", "fetus"],
"pediatrics": ["pediatr", "paediatr", "child", "infan", "newborn", "neonat", "congenital", "birth"],
"emergency": ["trauma", "injur", "poison", "shock", "burn", "emergen", "resuscit", "fracture", "wound"],
"orthopedics": ["bone", "joint", "muscl", "tendon", "ligament", "fracture", "osteo", "arthr", "skelet", "knee", "hip", "shoulder", "ankle", "vertebr"],
"psychiatry": ["psych", "mental", "depress", "anxiety", "schizo", "bipolar", "behavior", "behaviour", "panic", "stress disorder"]}
def map_specialties(term):
    out = set(term.get("specialties", []))
    label = term["en"].lower()
    for spec, prefixes in RULES.items():
        if any(tree.startswith(prefixes) for tree in term.get("trees", [])):
            out.add(spec)
    for spec, words in WORDS.items():
        if any(word in label for word in words):
            out.add(spec)
    for code in term.get("icd10_codes", []):
        if not code:
            continue
        letter = code[0]
        for s, letters in {"cardiology":"I", "pulmonology":"J", "gastroenterology":"K", "neurology":"G", "obgyn":"O", "orthopedics":"M", "psychiatry":"F", "pediatrics":"PQ", "emergency":"ST", "general_medicine":"R"}.items():
            if letter in letters:
                out.add(s)
        try:
            n = int(code[1:3])
            if letter == "N" and n <= 51:
                out.add("urology")
            if letter == "N" and 70 <= n <= 98:
                out.add("obgyn")
            if letter == "D" and 50 <= n <= 89:
                out.add("hematology")
        except ValueError:
            pass
    if term.get("semantic_type") == "anatomy":
        out.add("anatomy")
    if not out or term.get("frequency_rank", 9999) <= 2000:
        out.add("general_medicine")
    return sorted(out)
