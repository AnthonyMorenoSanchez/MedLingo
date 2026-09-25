import hashlib
import json
from datetime import UTC, datetime, timedelta

from app.db import active_profile, execute, one, rows
from app.engine.generators import REGISTRY
from app.schemas.questions import PAYLOADS

WRONG = "(s.last_result='wrong' OR s.wrong_count>s.correct_count OR (s.gave_up_count>0 AND s.streak<2))"
def now():
    return datetime.now(UTC).isoformat()
def update_schedule(stat, result, hinted=False, gave_up=False):
    stat=dict(stat)
    if result=="correct" and not gave_up:
        stat["streak"]+=1
        stat["ease"]=max(1.3,stat["ease"]+(0 if hinted else .1))
        stat["interval_days"]=1 if stat["streak"]==1 else 3 if stat["streak"]==2 else stat["interval_days"]*stat["ease"]
    else:
        stat["streak"]=0
        stat["ease"]=max(1.3,stat["ease"]-.2)
        stat["interval_days"]=0
    stat["due_at"]=(datetime.now(UTC)+timedelta(days=stat["interval_days"])).isoformat()
    return stat

def rule_query(rule, profile=None):
    profile = active_profile.get() if profile is None else profile
    where=["q.profile_id=:profile"]
    args={"profile":profile}
    for key,col in [("specialties","q.specialty_id"),("kinds","q.kind"),("item_ids","q.id")]:
        vals=rule.get(key,[])
        if vals:
            names=[]
            for i,v in enumerate(vals):
                param=f"{key}{i}";names.append(":"+param);args[param]=v
            where.append(col+" IN ("+",".join(names)+")")
    if rule.get("direction"):
        where.append("q.direction=:direction");args["direction"]=rule["direction"]
    filt=rule.get("result_filter")
    if filt=="wrong_only":where.append(WRONG)
    if filt=="correct_only":where.append("s.last_result='correct'")
    if filt=="leech":where.append("s.wrong_count>=5 AND s.correct_count<s.wrong_count")
    for key,col,op in [("min_wrong","s.wrong_count",">="),("max_ease","s.ease","<=")]:
        if rule.get(key) is not None:
            where.append(f"{col}{op}:{key}");args[key]=rule[key]
    if rule.get("seen_within_days") is not None:
        where.append("s.last_seen_at>=:since");args["since"]=(datetime.now(UTC)-timedelta(days=rule["seen_within_days"])).isoformat()
    return " AND ".join(where),args

def decode(item):
    return {**item,"payload":json.loads(item["payload"])}

def freeze(user, kind, direction, source, specialty, candidates, profile=None, sentence=False):
    profile = active_profile.get() if profile is None else profile
    term_id=None if sentence or kind=="encounter" else source["id"]
    sentence_id=source["id"] if sentence else None
    enc=source.get("encounter_id")
    node=source.get("id") if kind=="encounter" else None
    fingerprint=hashlib.sha1(f"{kind}|{direction}|{term_id}|{sentence_id}|{enc}|{node}".encode()).hexdigest()
    old=one(user,"SELECT * FROM question_items WHERE profile_id=:p AND fingerprint=:f",p=profile,f=fingerprint)
    if old:return old["id"]
    p=REGISTRY[kind]().generate(source,direction,f"{profile}|{fingerprint}",candidates)
    if kind in PAYLOADS:
        p=PAYLOADS[kind].model_validate(p).model_dump()
    result=execute(user,"INSERT INTO question_items(profile_id,kind,direction,term_id,sentence_id,encounter_id,node_id,specialty_id,payload,fingerprint,created_at) VALUES(:p,:k,:d,:t,:s,:e,:n,:sp,:payload,:f,:at)",p=profile,k=kind,d=direction,t=term_id,s=sentence_id,e=enc,n=node,sp=specialty,payload=json.dumps(p,ensure_ascii=False),f=fingerprint,at=now())
    item_id=result.lastrowid
    execute(user,"INSERT INTO item_stats(item_id,profile_id) VALUES(:i,:p)",i=item_id,p=profile)
    return item_id

def select_items(user,seed,request):
    count=request.count
    rule=request.model_dump()
    if request.mode=="bank":
        bank=one(user,"SELECT rule FROM banks WHERE id=:id AND profile_id=:active_profile",id=request.bank_id)
        if not bank:return []
        rule=json.loads(bank["rule"]);count=min(count,rule.get("limit",count))
    rule["result_filter"]={"wrong_test":"wrong_only","correct_drill":"correct_only"}.get(request.mode,rule.get("result_filter","any"))
    where,args=rule_query(rule)
    existing=[]
    if request.mode == "review":
        where+=" AND s.due_at<=:now";args["now"]=now()
    existing=[r["id"] for r in rows(user,"SELECT q.id FROM question_items q JOIN item_stats s ON q.id=s.item_id WHERE "+where+" ORDER BY RANDOM() LIMIT :lim",**args,lim=count)]
    if request.mode in ("wrong_test","correct_drill","bank") or request.item_ids:
        return existing[:count]
    if request.mode=="encounter":
        if not request.review_encounter and one(user,"SELECT id FROM question_items WHERE profile_id=:active_profile AND encounter_id=:e",e=request.encounter_id):
            from fastapi import HTTPException
            raise HTTPException(409,"This encounter has already been assigned. Select Review this encounter to repeat it.")
        enc=one(seed,"SELECT * FROM encounters WHERE id=:id",id=request.encounter_id)
        if not enc:return []
        graph=json.loads(enc["nodes"]);nodes={n["id"]:n for n in graph["nodes"]};key=graph["start"];ids=[]
        while not nodes[key].get("terminal"):
            n={**nodes[key],"encounter_id":enc["id"]}
            ids.append(freeze(user,"encounter",request.direction,n,enc["specialty_id"],[]))
            key=next(o["next"] for o in n["options"] if o["correct"])
        return ids
    # Reviews never silently introduce new content; new practice never reuses it.
    if request.mode == "review":
        return existing
    import random
    import unicodedata
    rng = random.SystemRandom()
    def normalized(value):
        return " ".join("".join(ch for ch in unicodedata.normalize("NFKC", value).casefold()
                                if ch.isalnum() or ch.isspace()).split())
    def keys(source):
        return {normalized(source["en"]), normalized(source["es"])}
    used = set()
    for row in rows(user, "SELECT payload FROM question_items WHERE profile_id=:active_profile"):
        payload = json.loads(row["payload"])
        for text in (payload.get("prompt", ""), payload.get("audio_text", ""),
                     payload.get("giveup", {}).get("answer_display", "")):
            if text:
                used.add(normalized(text))
    specialties = request.specialties or [r["id"] for r in rows(seed,"SELECT id FROM specialties")]
    pools: list[tuple[dict, str, bool]] = []
    for specialty in specialties:
        terms = rows(seed, "SELECT t.* FROM terms t JOIN term_specialties ts ON t.id=ts.term_id WHERE ts.specialty_id=:s AND t.difficulty BETWEEN :lo AND :hi", s=specialty,lo=request.difficulty_min,hi=request.difficulty_max)
        sentences = rows(seed, "SELECT * FROM sentences WHERE specialty_id=:s AND difficulty BETWEEN :lo AND :hi",s=specialty,lo=request.difficulty_min,hi=request.difficulty_max)
        for source in terms:
            for key in ("en_aliases", "es_aliases", "regional_notes"):
                if key in source:
                    source[key] = json.loads(source[key])
        pools.extend((source, specialty, False) for source in terms)
        pools.extend((source, specialty, True) for source in sentences)
    # Generated content is profile-owned and never changes the read-only seed bank.
    if one(user,"SELECT name FROM sqlite_master WHERE name='generated_content'"):
        for row in rows(user,"SELECT * FROM generated_content WHERE profile_id=:active_profile"):
            if row["specialty_id"] in specialties and request.difficulty_min <= row["difficulty"] <= request.difficulty_max:
                pools.append(({"id":-row["id"],"en":row["en"],"es":row["es"]},row["specialty_id"],True))
    rng.shuffle(pools)
    ids = []
    previous_kind = None
    candidate_cache = {}
    for source, specialty, sentence in pools:
        if len(ids) >= count:
            break
        if keys(source) & used:
            continue
        kinds = [k for k in request.kinds if k != "encounter" and (sentence or k != "drag_order")]
        rng.shuffle(kinds)
        kinds.sort(key=lambda k: k == previous_kind)
        lang = "es" if request.direction == "en2es" else "en"
        if specialty not in candidate_cache:
            candidate_cache[specialty] = [r[lang] for r in rows(seed,"SELECT t.en,t.es FROM terms t JOIN term_specialties ts ON t.id=ts.term_id WHERE ts.specialty_id=:s",s=specialty)]
        for kind in kinds:
            try:
                item = freeze(user,kind,request.direction,source,specialty,candidate_cache[specialty],sentence=sentence)
            except ValueError:
                continue
            ids.append(item)
            used.update(keys(source))
            previous_kind = kind
            break
    return ids
