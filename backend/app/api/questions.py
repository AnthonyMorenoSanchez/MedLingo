import json

from fastapi import APIRouter, HTTPException, Query, Request

from app.db import db, execute, one
from app.engine.scheduler import now

router = APIRouter()

from app.engine.hints import hint


@router.post("/items/{id}/hint",response_model=dict)
def get_hint(request: Request,id: int,level: int=Query(1,ge=1,le=4),session_id: int=Query(...)):
    with db(request.app) as c:
        item=one(c,"SELECT q.payload,s.mode FROM question_items q JOIN session_items si ON si.item_id=q.id JOIN sessions s ON s.id=si.session_id WHERE q.id=:id AND q.profile_id=:active_profile AND s.id=:session",id=id,session=session_id)
        if not item:raise HTTPException(404,"Item not found in this session")
        if item["mode"]=="wrong_test":raise HTTPException(403,"Hints are disabled during a test")
        execute(c,"UPDATE item_stats SET hint_count=hint_count+1 WHERE item_id=:id",id=id)
        return {"text":hint(json.loads(item["payload"]),level)}
@router.post("/content_issues",response_model=dict)
def report_issue(request: Request,body: dict):
    from pydantic import BaseModel, Field

    from app.config import ROOT
    class Issue(BaseModel):
        item_id: int
        note: str=Field(max_length=2000)
    issue=Issue.model_validate(body)
    with (ROOT/"docs/content_issues.jsonl").open("a") as f:
        f.write(json.dumps(dict(issue.model_dump(),ts=now()))+"\n")
    return {"ok":True}
