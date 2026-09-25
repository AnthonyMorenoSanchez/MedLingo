"""Refresh official snapshots, preserving the last good copy on failure."""
import json
import logging
import time
from datetime import UTC, datetime, timedelta

import httpx

from ingest.sources.base import FIXTURES


def refresh():
    FIXTURES.mkdir(exist_ok=True)
    log=[]
    classes={"disease":"Q12136","symptom":"Q169872","anatomy":"Q4936952","drug":"Q12140","procedure":"Q796194","test":"Q2671652"}
    with httpx.Client(timeout=60,headers={"User-Agent":"MedLingo/0.1 educational vocabulary trainer"}) as client:
        for kind,cls in classes.items():
            dest=FIXTURES/f"wikidata_{kind}.json"
            success=False
            for attempt in range(5):
                size=5000 if attempt==0 else 2000
                query='SELECT DISTINCT ?item ?en ?es ?icd ?tree WHERE { ?item wdt:P31/wdt:P279* wd:'+cls+'; rdfs:label ?en, ?es. FILTER(LANG(?en)="en" && LANG(?es)="es") OPTIONAL {?item wdt:P494 ?icd} OPTIONAL {?item wdt:P672 ?tree} } LIMIT '+str(size)
                try:
                    r=client.get("https://query.wikidata.org/sparql",params={"query":query,"format":"json"});r.raise_for_status()
                    data=r.json()
                    if len(data.get("results",{}).get("bindings",[]))>0:
                        dest.write_text(json.dumps(data,ensure_ascii=False))
                        success=True
                        break
                except (httpx.HTTPError, ValueError) as error:
                    logging.getLogger(__name__).warning("%s: %s",kind,error)
                time.sleep(min(2**attempt,8))
            log.append({"source":kind,"status":"fetched" if success else "fixture fallback", "at":datetime.now(UTC).isoformat()})
        for days in range(7):
            date=(datetime.now(UTC)-timedelta(days=days)).date().isoformat()
            try:
                r=client.get(f"https://medlineplus.gov/xml/mplus_topics_{date}.xml");r.raise_for_status()
                if b"<health-topics" in r.content:
                    (FIXTURES/"medlineplus_sample.xml").write_bytes(r.content)
                    break
            except httpx.HTTPError:
                continue
    (FIXTURES/"fetch_log.json").write_text(json.dumps(log,indent=2))
