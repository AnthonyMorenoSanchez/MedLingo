
from fastapi import APIRouter, Request

from app.db import db, one

router = APIRouter()

@router.get("/health",response_model=dict)
def health(request: Request):
    with db(request.app,True) as c:
        return {"status":"ok","seed_built_at":one(c,"SELECT value FROM seed_meta WHERE key='built_at'")["value"],"term_count":one(c,"SELECT count(*) n FROM terms")["n"],"uptime_s":request.app.state.uptime()}
