import json

from fastapi import APIRouter, HTTPException, Request

from app.db import db, one, rows

router = APIRouter()

@router.get("/encounters",response_model=list[dict])
def encounters(request: Request,specialty: str=""):
    with db(request.app,True) as c:return rows(c,"SELECT id,title_en,title_es,specialty_id,difficulty FROM encounters WHERE (:s='' OR specialty_id=:s) ORDER BY title_en",s=specialty)
@router.get("/encounters/{id}",response_model=dict)
def encounter(request: Request,id: str):
    with db(request.app,True) as c:
        enc=one(c,"SELECT * FROM encounters WHERE id=:id",id=id)
        if not enc:raise HTTPException(404,"Encounter not found")
        enc["nodes"]=json.loads(enc["nodes"])
        return enc
