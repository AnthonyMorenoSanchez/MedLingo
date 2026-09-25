import json

from fastapi import APIRouter, HTTPException, Request

from app.db import db, execute, one, rows
from app.engine.scheduler import now

router = APIRouter()

from app.engine.scheduler import rule_query
from app.schemas.banks import BankInput, BankRule


def count_rule(c,rule):
    where,args=rule_query(rule)
    n=one(c,"SELECT count(*) n FROM question_items q JOIN item_stats s ON s.item_id=q.id WHERE "+where,**args)["n"]
    return min(n,rule.get("limit",40))
@router.get("/banks",response_model=list[dict])
def banks(request: Request):
    with db(request.app) as c:
        banks=rows(c,"SELECT * FROM banks WHERE profile_id=:active_profile ORDER BY id DESC")
        for b in banks:b["rule"]=json.loads(b["rule"]);b["count"]=count_rule(c,b["rule"])
        return banks
@router.post("/banks",response_model=dict)
def create(request: Request,body: BankInput):
    with db(request.app) as c:
        result=execute(c,"INSERT INTO banks(profile_id,name,rule,created_at) VALUES(:active_profile,:n,:r,:t)",n=body.name,r=body.rule.model_dump_json(),t=now())
        return {"id":result.lastrowid,**body.model_dump()}
@router.post("/banks/preview",response_model=dict)
def preview(request: Request,body: BankRule):
    with db(request.app) as c:return {"count":count_rule(c,body.model_dump())}
@router.delete("/banks/{id}",response_model=dict)
def delete(request: Request,id: int):
    with db(request.app) as c:
        if not execute(c,"DELETE FROM banks WHERE id=:id AND profile_id=:active_profile",id=id).rowcount:raise HTTPException(404,"Bank not found")
        return {"ok":True}
