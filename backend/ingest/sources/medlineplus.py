from lxml import etree

from ingest.sources.base import FIXTURES, BaseSource


class MedlinePlus(BaseSource):
    def terms(self, offline=True):
        root = etree.parse(str(FIXTURES / "medlineplus_sample.xml"), etree.XMLParser(resolve_entities=False, no_network=True))
        for topic in root.findall("health-topic"):
            if topic.get("language") != "English":
                continue
            mapped = topic.find("language-mapped-topic")
            if mapped is not None and mapped.get("language") == "Spanish":
                yield {"en": topic.get("title"), "es": mapped.text, "source": "medlineplus", "source_id": topic.get("url"), "en_aliases": [x.text for x in topic.findall("also-called")], "semantic_type": "other", "pos": "phrase", "mesh_ids": [x.get("id") for x in topic.findall("mesh-heading/descriptor")]}
