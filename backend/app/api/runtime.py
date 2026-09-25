
from fastapi import APIRouter, Request

from app.db import db, one

router = APIRouter()

from datetime import UTC, datetime


@router.get("/runtime",response_model=dict)
def runtime(request: Request):
    with db(request.app) as c:
        result=one(c,"SELECT count(*) n,coalesce(sum((julianday(last_heartbeat_at)-julianday(process_started_at))*86400),0) total FROM runtime_log")
        current=one(c,"SELECT * FROM runtime_log WHERE id=:id",id=request.app.state.runtime_id)
        extra=max(0,(datetime.now(UTC)-datetime.fromisoformat(current["last_heartbeat_at"])).total_seconds())
        return {"current_uptime_s":request.app.state.uptime(),"total_runtime_s":result["total"]+extra,"restarts":max(0,result["n"]-1)}
