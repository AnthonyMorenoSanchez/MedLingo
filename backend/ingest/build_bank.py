import argparse
import hashlib
import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import yaml

from app.config import Settings
from app.engine.templates import TemplateRenderError, expand_slots, render
from ingest.dedupe import dedupe
from ingest.gender import infer
from ingest.sources.curated import CURATED, Curated, load
from ingest.sources.decs import DeCS
from ingest.sources.medlineplus import MedlinePlus
from ingest.sources.wikidata import Wikidata
from ingest.sources.wiktionary import enrich
from ingest.specialty_map import map_specialties

SOURCES: dict = {"wikidata": Wikidata, "decs": DeCS, "medlineplus": MedlinePlus, "curated": Curated}
def stable_id(value):
    return int(hashlib.sha256(value.encode()).hexdigest()[:13], 16)

def validate_encounter(graph):
    nodes = {n["id"]: n for n in graph["nodes"]}
    if len(nodes) != len(graph["nodes"]):
        raise ValueError("Duplicate node ID")
    seen, active = set(), set()
    def visit(key):
        if key in active:
            raise ValueError("Encounter cycle")
        if key not in nodes:
            raise ValueError("Dangling next node")
        if key in seen:
            return
        active.add(key)
        node = nodes[key]
        if not node.get("terminal"):
            correct = [o for o in node["options"] if o.get("correct")]
            if len(correct) != 1 or not correct[0].get("next"):
                raise ValueError("Each node needs one advancing correct option")
            for option in node["options"]:
                if option.get("next"):
                    visit(option["next"])
        seen.add(key)
        active.remove(key)
    visit(graph["start"])
    if not any(nodes[n].get("terminal") for n in seen):
        raise ValueError("No reachable terminal")
    if seen != set(nodes):
        raise ValueError("Unreachable nodes")

def build(output=None, offline=True, sources=None, limit=None):
    output = Path(output or Settings().path("seed_db"))
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(".building.sqlite")
    tmp.unlink(missing_ok=True)
    conn = sqlite3.connect(tmp)
    conn.executescript((Path(__file__).resolve().parents[1]/"app/models/seed.sql").read_text())
    for s in load("specialties.yaml"):
        conn.execute("INSERT INTO specialties VALUES(:id,:name_en,:name_es,:color,:icon,:sort_order)", s)
    terms = dedupe(t for source in (sources or list(SOURCES)) for t in SOURCES[source]().terms(offline))
    terms = list(enrich(terms))
    overrides = load("term_overrides.yaml")
    blacklist = set(overrides["blacklist"])
    notes = load("regional_notes.yaml")
    skipped = 0
    term_groups: dict = {}
    for rank, t in enumerate(terms[:limit] if limit else terms, 1):
        if t["en"] in blacklist or t["es"] in blacklist:
            continue
        t["frequency_rank"] = (1 if t.get("pos","noun")=="noun" else 200) if t["source"] == "curated" else rank+500
        t["id"] = stable_id(t["en"]+"|"+t["es"])
        t["pos"] = t.get("pos", "noun")
        t["gender_es"] = t.get("gender_es") or (infer(t["es"]) if t["pos"] == "noun" else None)
        t["number_es"] = t.get("number_es", "pl" if t["es"] in ("heces", "signos vitales") else "sg")
        t["semantic_type"] = t.get("semantic_type", "other")
        t["difficulty"] = t.get("difficulty", 3)
        conn.execute("INSERT INTO terms(id,en,es,en_aliases,es_aliases,pos,gender_es,number_es,semantic_type,definition_en,definition_es,frequency_rank,difficulty,source,source_id,regional_notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (t["id"],t["en"],t["es"],json.dumps(t.get("en_aliases", [])),json.dumps(t.get("es_aliases", [])),t["pos"],t["gender_es"],t["number_es"],t["semantic_type"],t.get("definition_en"),t.get("definition_es"),t["frequency_rank"],t["difficulty"],t["source"],t.get("source_id"),json.dumps(notes.get(t["es"], []),ensure_ascii=False)))
        for specialty in map_specialties(t):
            conn.execute("INSERT INTO term_specialties VALUES(?,?)", (t["id"],specialty))
            term_groups.setdefault(specialty, []).append(t)
    for path in sorted((CURATED / "templates").glob("*.yaml")):
        for template in yaml.safe_load(path.read_text()):
            tid = stable_id(template["key"])
            specialty = template["specialty"]
            conn.execute("INSERT INTO templates VALUES(?,?,?,?,?,?,?,?)", (tid,template["key"],template["en"],template["es"],json.dumps(template["slots"]),specialty,template["difficulty"],template["register"]))
            for selected in expand_slots(template, term_groups):
                try:
                    en,es = render(template["en"],selected,"en"),render(template["es"],selected)
                except TemplateRenderError:
                    skipped += 1
                    continue
                slots=[]
                for key,term in selected.items():
                    position=es.find(term["es"])
                    slots.append({"slot":key,"term_id":term.get("id"),"es_surface":term["es"],"en_surface":term["en"],"start_es":position,"end_es":position+len(term["es"])})
                conn.execute("INSERT OR IGNORE INTO sentences VALUES(?,?,?,?,?,?,?,?)", (stable_id(en+"|"+es),tid,en,es,json.dumps(slots),specialty,2,"curated"))
    for path in sorted((CURATED/"phrases").glob("*.yaml")):
        for p in yaml.safe_load(path.read_text()):
            conn.execute("INSERT OR IGNORE INTO sentences VALUES(?,?,?,?,?,?,?,?)",(stable_id(p["en"]+"|"+p["es"]),None,p["en"],p["es"],"[]",p["specialty"],p["difficulty"],"curated"))
    for path in sorted((CURATED/"encounters").glob("*.yaml")):
        graph = yaml.safe_load(path.read_text())
        validate_encounter(graph)
        conn.execute("INSERT INTO encounters VALUES(?,?,?,?,?,?)",(graph["id"],graph["title_en"],graph["title_es"],graph["specialty"],graph["difficulty"],json.dumps(graph,ensure_ascii=False)))
    meta={"built_at":datetime.now(UTC).isoformat(),"mode":"offline" if offline else "online", "skipped_unknown_gender":str(skipped), "sources":"Wikidata downloaded snapshots; MedlinePlus 2026-09-12; Wiktionary 300 lookups; curated 0.1; DeCS unavailable (HTTP 403)"}
    conn.executemany("INSERT INTO seed_meta VALUES(?,?)",meta.items())
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    os.replace(tmp, output)
    from ingest.report import report
    return report(output)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--offline",action="store_true")
    p.add_argument("--output")
    p.add_argument("--limit",type=int)
    p.add_argument("--sources")
    p.add_argument("--dump-fixtures",action="store_true")
    args=p.parse_args()
    if not args.offline:
        from ingest.fetch import refresh
        refresh()
    result=build(args.output,args.offline,args.sources.split(",") if args.sources else None,args.limit)
    print(json.dumps(result,indent=2))
    if not result["pass"]:
        raise SystemExit(1)
if __name__ == "__main__":
    main()
