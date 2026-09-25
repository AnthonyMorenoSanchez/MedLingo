from rapidfuzz.distance.Levenshtein import distance

from app.engine.normalize import normalize


def choose(answer, candidates, rng, count=3):
    candidates = sorted(set(candidates))
    rng.shuffle(candidates)
    selected: list[str] = []
    for candidate in candidates:
        norm = normalize(candidate, accents=True)
        existing = [normalize(x, accents=True) for x in [answer, *selected]]
        if all(norm[:4] != x[:4] and distance(norm, x) >= 3 for x in existing):
            selected.append(candidate)
            if len(selected) == count:
                return selected
    raise ValueError("Insufficient distinct distractors")
