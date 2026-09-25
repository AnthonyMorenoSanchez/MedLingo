
from fastapi import APIRouter, HTTPException, Query, Request

from app.db import db, execute, one, rows
from app.engine.scheduler import now

router = APIRouter()

from app.engine.scheduler import decode, select_items
from app.schemas.questions import SessionBatch, SessionInput


def get_session(c,id):
    session=one(c,"SELECT * FROM sessions WHERE id=:id AND profile_id=:active_profile",id=id)
    if not session:raise HTTPException(404,"Session not found")
    return session

def batch(c,id,after=None):
    session=get_session(c,id)
    position=-1
    if after is not None:
        row=one(c,"SELECT position FROM session_items WHERE session_id=:s AND item_id=:i",s=id,i=after)
        if not row:raise HTTPException(400,"Cursor not in session")
        position=row["position"]
    items=rows(c,"SELECT q.* FROM session_items si JOIN question_items q ON q.id=si.item_id WHERE si.session_id=:s AND si.position>:p AND NOT EXISTS(SELECT 1 FROM attempts a WHERE a.session_id=si.session_id AND a.item_id=si.item_id) ORDER BY si.position LIMIT 20",s=id,p=position)
    return {"session":session,"items":[decode(i) for i in items]}

@router.post("/sessions",response_model=SessionBatch)
def create_session(request: Request,body: SessionInput):
    with db(request.app) as c,db(request.app,True) as seed:
        execute(c,"BEGIN IMMEDIATE")
        ids=select_items(c,seed,body)
        if not ids:
            raise HTTPException(409, "No fresh material remains for these filters. Choose Review, change filters, or generate new material in AI settings." if body.mode=="learn" else "No matching review items are available.")
        stamp=now()
        result=execute(c,"INSERT INTO sessions(profile_id,mode,filters,started_at,last_heartbeat_at,planned_count) VALUES(:active_profile,:m,:f,:t,:t,:n)",m=("wrong_test" if body.test_mode else body.mode),f=body.model_dump_json(),t=stamp,n=len(ids))
        sid=result.lastrowid
        for i,item in enumerate(ids):execute(c,"INSERT INTO session_items VALUES(:s,:i,:p)",s=sid,i=item,p=i)
        return batch(c,sid)
@router.get("/sessions/{id}/next",response_model=SessionBatch)
def next_batch(request: Request,id: int,after_item_id: int | None=None):
    with db(request.app) as c:return batch(c,id,after_item_id)
@router.post("/sessions/{id}/heartbeat",response_model=dict)
def heartbeat(request: Request,id: int):
    with db(request.app) as c:
        s=get_session(c,id)
        if not s["ended_at"]:execute(c,"UPDATE sessions SET last_heartbeat_at=:t WHERE id=:id",t=now(),id=id)
        return {"ok":True}
@router.post("/sessions/{id}/end",response_model=dict)
def end(request: Request,id: int):
    with db(request.app) as c:
        s=get_session(c,id)
        if not s["ended_at"]:
            bonus=25 if s["planned_count"]>0 and s["completed_count"]==s["planned_count"] else 0
            execute(c,"UPDATE sessions SET ended_at=:t,last_heartbeat_at=:t,xp_earned=xp_earned+:bonus WHERE id=:id",id=id,t=now(),bonus=bonus)
        return summary_data(c,id)
def summary_data(c,id):
    s=get_session(c,id)
    s["attempts"]=rows(c,"SELECT a.*,q.kind,q.payload FROM attempts a JOIN question_items q ON q.id=a.item_id WHERE a.session_id=:id ORDER BY a.id",id=id)
    s["time_ms"]=sum(a["time_ms"] for a in s["attempts"])
    return s
@router.get("/sessions/{id}",response_model=dict)
def summary(request: Request,id: int):
    with db(request.app) as c:return summary_data(c,id)
@router.get("/sessions",response_model=list[dict])
def history(request: Request,limit: int=Query(20,ge=1,le=100)):
    with db(request.app) as c:return rows(c,"SELECT * FROM sessions WHERE profile_id=:active_profile ORDER BY id DESC LIMIT :n",n=limit)
