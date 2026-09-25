import json

from fastapi import APIRouter, HTTPException, Query, Request

from app.db import db, one, rows

router = APIRouter()

@router.get("/terms",response_model=dict)
def terms(request: Request,specialty: str="",q: str="",page: int=Query(1,ge=1),size: int=Query(30,ge=1,le=100)):
    with db(request.app,True) as c:
        where="(en LIKE :q OR es LIKE :q) AND (:s='' OR EXISTS(SELECT 1 FROM term_specialties ts WHERE ts.term_id=t.id AND ts.specialty_id=:s))"
        return {"items":rows(c,"SELECT * FROM terms t WHERE "+where+" ORDER BY frequency_rank,id LIMIT :n OFFSET :o",q="%"+q+"%",s=specialty,n=size,o=(page-1)*size),"total":one(c,"SELECT count(*) n FROM terms t WHERE "+where,q="%"+q+"%",s=specialty)["n"],"page":page}
@router.get("/terms/{id}",response_model=dict)
def term(request: Request,id: int):
    with db(request.app,True) as c:
        t=one(c,"SELECT * FROM terms WHERE id=:id",id=id)
        if not t:raise HTTPException(404,"Term not found")
        for key in ("en_aliases","es_aliases","regional_notes"):t[key]=json.loads(t[key])
        t["examples"]=rows(c,"SELECT en,es FROM sentences WHERE slots LIKE :id LIMIT 5",id="%"+str(id)+"%")
        return t
