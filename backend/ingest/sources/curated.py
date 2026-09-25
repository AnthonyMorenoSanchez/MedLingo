from pathlib import Path

import yaml

from ingest.sources.base import BaseSource

CURATED = Path(__file__).resolve().parents[1] / "curated"

def load(name):
    return yaml.safe_load((CURATED / name).read_text())

class Curated(BaseSource):
    def terms(self, offline=True):
        yield from load("term_overrides.yaml")["add"]
        for path in sorted((CURATED / "phrases").glob("*.yaml")):
            for row in yaml.safe_load(path.read_text()):
                yield dict(row, source="curated", pos="phrase", semantic_type="phrase", specialties=[row["specialty"], "patient_phrases"])
