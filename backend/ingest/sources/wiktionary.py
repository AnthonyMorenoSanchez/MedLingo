import json

from ingest.sources.base import FIXTURES


def enrich(terms):
    path = FIXTURES / "wiktionary_sample.json"
    lookup = json.loads(path.read_text()) if path.exists() else {}
    for term in terms:
        if term["es"] in lookup:
            term.update(lookup[term["es"]])
        yield term
