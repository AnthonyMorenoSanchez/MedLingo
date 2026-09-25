import json

from ingest.sources.base import FIXTURES, BaseSource


class Wikidata(BaseSource):
    def terms(self, offline=True):
        for path in sorted(FIXTURES.glob("wikidata_*.json")):
            data = json.loads(path.read_text())
            kind = path.stem.removeprefix("wikidata_")
            if kind == "sample":
                continue
            for row in data.get("results", {}).get("bindings", []):
                value = lambda key, row=row: row.get(key, {}).get("value", "")
                if not value("en") or not value("es"):
                    continue
                yield {"en": value("en"), "es": value("es"), "source": "wikidata", "source_id": value("item"), "semantic_type": kind, "trees": [value("tree")], "icd10_codes": [value("icd")], "mesh_ids": [value("mesh")]}
