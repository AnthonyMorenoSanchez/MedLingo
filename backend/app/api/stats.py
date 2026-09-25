import json

from fastapi import APIRouter, Query, Request

from app.db import db, one, rows

router = APIRouter()

from datetime import UTC, datetime, timedelta

from app.engine.scheduler import rule_query


@router.get("/review",response_model=dict)
def review(request: Request,tab: str="wrong",specialty: str="",kind: str="",direction: str="",q: str="",page: int=Query(1,ge=1)):
    rule={"result_filter":{"wrong":"wrong_only","correct":"correct_only","leech":"leech"}.get(tab,"any"),"specialties":[specialty] if specialty else [],"kinds":[kind] if kind else [],"direction":direction}
    where,args=rule_query(rule)
    where+=" AND q.payload LIKE :search";args["search"]="%"+q+"%"
    with db(request.app) as c:
        items=rows(c,"SELECT q.*,s.correct_count,s.wrong_count,s.last_seen_at,s.total_time_ms,s.attempts,s.gave_up_count FROM question_items q JOIN item_stats s ON s.item_id=q.id WHERE "+where+" ORDER BY s.last_seen_at DESC LIMIT 30 OFFSET :off",**args,off=(page-1)*30)
        for i in items:i["payload"]=json.loads(i["payload"])
        return {"items":items,"total":one(c,"SELECT count(*) n FROM question_items q JOIN item_stats s ON s.item_id=q.id WHERE "+where,**args)["n"],"page":page}
@router.get("/stats/overview",response_model=dict)
def overview(request: Request,day: str=""):
    today=day or datetime.now(UTC).date().isoformat()
    with db(request.app) as c:
        attempts=one(c,"SELECT count(*) n,coalesce(sum(result='correct'),0) correct,coalesce(sum(time_ms),0) active_ms FROM attempts WHERE profile_id=:active_profile")
        total=one(c,"SELECT coalesce(sum(max(0,(julianday(last_heartbeat_at)-julianday(started_at))*86400000)),0) ms,coalesce(sum(xp_earned),0) xp FROM sessions WHERE profile_id=:active_profile")
        daily=one(c,"SELECT * FROM daily_stats WHERE profile_id=:active_profile AND day=:d",d=today) or {"study_ms":0}
        recent=one(c,"SELECT count(*) n,coalesce(sum(result='correct'),0) correct FROM attempts WHERE profile_id=:active_profile AND ts>=:since",since=(datetime.now(UTC)-timedelta(days=7)).isoformat())
        days={x["day"] for x in rows(c,"SELECT day FROM daily_stats WHERE profile_id=:active_profile AND attempts>0 ORDER BY day DESC LIMIT 366")}
        streak=0;d=datetime.fromisoformat(today).date()
        if d.isoformat() not in days:d-=timedelta(days=1)
        while d.isoformat() in days:streak+=1;d-=timedelta(days=1)
        return {"total_study_ms":total["ms"],"today_ms":daily["study_ms"],"active_ms":attempts["active_ms"],"attempts":attempts["n"],"correct":attempts["correct"],"accuracy":attempts["correct"]/max(1,attempts["n"])*100,"accuracy_7d":recent["correct"]/max(1,recent["n"])*100,"xp":total["xp"],"level":1+int(total["xp"]/500),"streak":streak}
@router.get("/stats/specialties",response_model=list[dict])
def specialty_stats(request: Request):
    with db(request.app) as c:return rows(c,"SELECT q.specialty_id, count(*) items_seen,sum(s.correct_count) correct,sum(s.wrong_count) wrong,CASE WHEN sum(s.correct_count)>=500 THEN 500 WHEN sum(s.correct_count)>=200 THEN 200 WHEN sum(s.correct_count)>=50 THEN 50 ELSE 0 END badge,100.0*sum(s.correct_count)/max(1,sum(s.attempts)) accuracy FROM question_items q JOIN item_stats s ON s.item_id=q.id WHERE q.profile_id=:active_profile AND s.attempts>0 GROUP BY q.specialty_id")
@router.get("/stats/time",response_model=dict)
def time_stats(request: Request,from_: str=Query("",alias="from"),to: str="9999"):
    with db(request.app) as c:
        daily=rows(c,"SELECT * FROM daily_stats WHERE profile_id=:active_profile AND day>=:f AND day<=:t ORDER BY day",f=from_,t=to)
        histogram=[]
        for label,lo,hi in [("0-5s",0,5000),("5-10s",5000,10000),("10-20s",10000,20000),("20-40s",20000,40000),("40+s",40000,86400001)]:
            histogram.append({"bucket":label,"count":one(c,"SELECT count(*) n FROM attempts WHERE profile_id=:active_profile AND time_ms>=:lo AND time_ms<:hi",lo=lo,hi=hi)["n"]})
        return {"daily":daily,"histogram":histogram}
@router.get("/stats/wrong_trend",response_model=list[dict])
def wrong_trend(request: Request):
    with db(request.app) as c:
        # Last result per item at each day's close, based on stored attempts.
        return rows(c,"WITH days AS (SELECT DISTINCT substr(ts,1,10) day FROM attempts WHERE profile_id=:active_profile), latest AS (SELECT d.day,a.item_id,max(a.id) id FROM days d JOIN attempts a ON substr(a.ts,1,10)<=d.day AND a.profile_id=:active_profile GROUP BY d.day,a.item_id) SELECT l.day,sum(a.result='wrong') count FROM latest l JOIN attempts a ON a.id=l.id GROUP BY l.day ORDER BY l.day")
