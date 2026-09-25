
from fastapi import APIRouter, Request

from app.db import db, rows

router = APIRouter()

@router.get("/specialties",response_model=list[dict])
def specialties(request: Request):
    with db(request.app,True) as c:
        return rows(c,"SELECT s.*, (SELECT count(*) FROM term_specialties ts WHERE ts.specialty_id=s.id) term_count FROM specialties s ORDER BY sort_order")
