from lxml import etree

from ingest.sources.base import FIXTURES, BaseSource


class DeCS(BaseSource):
    def terms(self, offline=True):
        path = FIXTURES / "decs_sample.xml"
        if not path.exists():
            return
        root = etree.parse(str(path), etree.XMLParser(resolve_entities=False, no_network=True))
        for record in root.findall(".//record"):
            en, es = record.findtext("en"), record.findtext("es")
            if en and es:
                yield {"en": en, "es": es, "source": "decs", "source_id": record.get("id"), "trees": [t.text for t in record.findall("tree")]}
