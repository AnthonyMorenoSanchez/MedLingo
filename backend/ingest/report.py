import argparse
import json
import sqlite3
from pathlib import Path

from app.config import Settings


def report(path=None):
    path = Path(path or Settings().path("seed_db"))
    c=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    meta=dict(c.execute("SELECT key,value FROM seed_meta"))
    counts={k:c.execute(f"SELECT count(*) FROM {k}").fetchone()[0] for k in ("terms","sentences","encounters")}
    noun,known=c.execute("SELECT count(*),sum(gender_es IS NOT NULL) FROM terms WHERE pos='noun'").fetchone()
    coverage=(known or 0)/max(noun,1)
    per=[]
    checks={"total terms":counts["terms"] >= (2500 if meta["mode"]=="offline" else 6000), "sentences": counts["sentences"] >= (1500 if meta["mode"]=="offline" else 3000), "12 encounters":counts["encounters"]==12, "noun gender >= 85%":coverage >= .85, "unique pairs":c.execute("SELECT count(*) FROM (SELECT en,es FROM terms GROUP BY en,es HAVING count(*)>1)").fetchone()[0]==0}
    for (s,) in c.execute("SELECT id FROM specialties ORDER BY sort_order"):
        n=c.execute("SELECT count(*) FROM term_specialties WHERE specialty_id=?",(s,)).fetchone()[0]
        nsen=c.execute("SELECT count(*) FROM sentences WHERE specialty_id=?",(s,)).fetchone()[0]
        enc=c.execute("SELECT count(*) FROM encounters WHERE specialty_id=?",(s,)).fetchone()[0]
        per.append((s,n,nsen,enc))
        checks[s+" terms"]= n >= (400 if s=="anatomy" else 300 if s=="patient_phrases" else 200)
        checks[s+" sentences"]=nsen >= 80
    text="# Bank report\n\nBuilt: "+meta["built_at"]+"\n\n"+json.dumps(counts)+f"\n\nKnown noun gender: {coverage:.1%}\n\n| Specialty | Terms | Sentences | Encounters |\n|---|---:|---:|---:|\n"
    text += "\n".join("| "+" | ".join(map(str,row))+" |" for row in per)
    text += "\n\n| Threshold | Result |\n|---|---|\n"+"\n".join(f"| {k} | {'PASS' if v else 'FAIL'} |" for k,v in checks.items())
    for table,column in [("terms","source"),("terms","semantic_type")]:
        text+=f"\n\nCounts by {column}: "+json.dumps(dict(c.execute(f"SELECT {column},count(*) FROM {table} GROUP BY {column}")))
    text+='\n\n'+json.dumps(meta)
    for s,*_ in per:
        text+=f"\n\n## {s} sample\n\n| English | Spanish | Source |\n|---|---|---|\n"
        text+='\n'.join('| '+' | '.join(row)+' |' for row in c.execute("SELECT en,es,source FROM terms JOIN term_specialties ts ON ts.term_id=terms.id WHERE ts.specialty_id=? ORDER BY terms.id LIMIT 20",(s,)))
    path.with_name("bank_report.md").write_text(text+"\n")
    c.close()
    return dict(counts, gender_coverage=coverage,pass_=all(checks.values()), **{"pass":all(checks.values()),"checks":checks})
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.parse_args()
    result=report();print(json.dumps(result,indent=2));raise SystemExit(0 if result["pass"] else 1)
