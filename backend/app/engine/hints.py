def hint(payload, level=1):
    answer = payload["giveup"]["answer_display"]
    hints = [answer[:1] + " " + "_ " * max(0, len(answer)-1), payload.get("gender_hint", "Listen to the pronunciation and identify the word ending."), payload.get("alias_hint") or "Think of a synonym for the source phrase.", payload["giveup"]["explanation_en"]]
    return hints[min(max(level, 1), 4)-1]
