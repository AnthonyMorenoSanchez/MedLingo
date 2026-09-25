def score(messages):
    text=" ".join(m["content"].lower() for m in messages if m["role"]=="user")
    return {"empathy_phrases":sum(p in text for p in ("entiendo","siento","comprendo","preocupa","por favor")),"terminology":sum(p in text for p in ("dolor","síntoma","medicamento","alergia","cuándo","desde")),"user_words":len(text.split())}
