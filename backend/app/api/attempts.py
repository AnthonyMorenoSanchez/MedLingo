import json

from fastapi import APIRouter, HTTPException, Request

from app.db import db, execute, one
from app.engine.scheduler import now

router = APIRouter()

from app.api.sessions import get_session
from app.engine.normalize import check
from app.engine.scheduler import update_schedule
from app.schemas.attempts import AttemptInput, AttemptResult


@router.post("/attempts",response_model=AttemptResult)
def submit(request: Request,body: AttemptInput):
    with db(request.app) as c:
        execute(c,"BEGIN IMMEDIATE")
        session=get_session(c,body.session_id)
        item=one(c,"SELECT q.* FROM question_items q JOIN session_items si ON si.item_id=q.id WHERE q.profile_id=:active_profile AND q.id=:i AND si.session_id=:s",i=body.item_id,s=body.session_id)
        if not item:raise HTTPException(400,"Item does not belong to session")
        existing=one(c,"SELECT id FROM attempts WHERE item_id=:i AND session_id=:s",i=body.item_id,s=body.session_id)
        if existing:raise HTTPException(409,"This item has already been answered in this session")
        if session["ended_at"]:raise HTTPException(409,"Session has ended")
        if session["mode"]=="wrong_test" and body.hint_used:raise HTTPException(400,"Hints are disabled during a test")
        p=json.loads(item["payload"])
        answer=p["giveup"]["answer_display"]
        if body.gave_up:result,feedback="wrong","gave_up"
        elif item["kind"] in ("mcq","drag_slot","encounter"):
            correct_id=p.get("answer_id",p.get("correct_id"))
            result="correct" if body.answer_given==correct_id else "wrong"
            feedback=p.get("feedback",{}).get(body.answer_given,"exact" if result=="correct" else "incorrect") if isinstance(p.get("feedback",{}),dict) else "incorrect"
        else:result,feedback=check(body.answer_given,[answer,*p.get("accepted",[])],p.get("article_required",False))
        xp=0 if result=="wrong" else 2 if feedback=="accents" else 5 if body.hint_used else 10
        profile=json.loads(one(c,"SELECT settings FROM profiles WHERE id=:active_profile")["settings"])
        goal_ms=max(1,min(180,int(profile.get("daily_goal",15))))*60000
        previous=one(c,"SELECT study_ms FROM daily_stats WHERE profile_id=:active_profile AND day=:d",d=body.client_day.isoformat())
        previous_ms=previous["study_ms"] if previous else 0
        if previous_ms<goal_ms<=previous_ms+body.time_ms:
            xp+=15

        execute(c,"INSERT INTO attempts(item_id,session_id,result,answer_given,time_ms,hint_used,gave_up,ts,profile_id) VALUES(:i,:s,:r,:a,:ms,:h,:g,:t,:active_profile)",i=body.item_id,s=body.session_id,r=result,a=body.answer_given,ms=body.time_ms,h=int(body.hint_used),g=int(body.gave_up),t=now())
        stat=one(c,"SELECT * FROM item_stats WHERE item_id=:id AND profile_id=:active_profile",id=body.item_id)
        stat=update_schedule(stat,result,body.hint_used,body.gave_up)
        execute(c,"UPDATE item_stats SET correct_count=correct_count+:correct,wrong_count=wrong_count+:wrong,gave_up_count=gave_up_count+:gave,streak=:streak,ease=:ease,interval_days=:interval,due_at=:due,last_result=:result,last_seen_at=:at,total_time_ms=total_time_ms+:ms,attempts=attempts+1 WHERE item_id=:id",correct=int(result=="correct"),wrong=int(result=="wrong"),gave=int(body.gave_up),streak=stat["streak"],ease=stat["ease"],interval=stat["interval_days"],due=stat["due_at"],result=result,at=now(),ms=body.time_ms,id=body.item_id)
        execute(c,"UPDATE sessions SET completed_count=completed_count+1,correct_count=correct_count+:correct,xp_earned=xp_earned+:xp,last_heartbeat_at=:at WHERE id=:s",correct=int(result=="correct"),xp=xp,at=now(),s=body.session_id)
        execute(c,"INSERT INTO daily_stats(profile_id,day,study_ms,attempts,correct,xp) VALUES(:active_profile,:day,:ms,1,:correct,:xp) ON CONFLICT(profile_id,day) DO UPDATE SET study_ms=study_ms+:ms,attempts=attempts+1,correct=correct+:correct,xp=xp+:xp",day=body.client_day.isoformat(),ms=body.time_ms,correct=int(result=="correct"),xp=xp)
        return {"result":result,"feedback":feedback,"correct_answer":answer,"stats_after":one(c,"SELECT * FROM item_stats WHERE item_id=:id",id=body.item_id),"xp":xp}
