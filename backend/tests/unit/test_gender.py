import yaml

from ingest.gender import infer
from ingest.sources.curated import CURATED


def test_labeled_nouns():
    labeled=yaml.safe_load((CURATED/"term_overrides.yaml").read_text())["add"]
    assert len(labeled)>=200
    assert sum(infer(t["es"])==t["gender_es"] for t in labeled)/len(labeled)>=.9

def test_heuristics():
    assert infer("ventilación")=="f"
    assert infer("ventilador")=="m"
    assert infer("arterias")=="f"
    assert infer("síndromes")=="m"
    assert infer("xyz")==None
