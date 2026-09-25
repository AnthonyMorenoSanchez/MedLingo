import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.db import active_profile, db, execute, one, rows
from app.engine.scheduler import now

router = APIRouter()
class ProfileInput(BaseModel):
    name: str = Field(min_length=1, max_length=60)

@router.get('/profiles')
def profiles(request: Request):
    with db(request.app) as c:
        return rows(c, 'SELECT id,name FROM profiles ORDER BY id')

@router.post('/profiles')
def create(request: Request, body: ProfileInput):
    name = body.name.strip()
    if not name:
        raise HTTPException(422, 'Enter a profile name')
    with db(request.app) as c:
        if one(c, 'SELECT id FROM profiles WHERE lower(name)=lower(:n)', n=name):
            raise HTTPException(409, 'That profile name already exists')
        pid = execute(c, "INSERT INTO profiles(name,settings,created_at) VALUES(:n,'{}',:t)", n=name,t=now()).lastrowid
        return {'id':pid,'name':name,'settings':{}}

@router.get('/profiles/current')
def profile(request: Request):
    with db(request.app) as c:
        row=one(c,'SELECT * FROM profiles WHERE id=:active_profile')
        row['settings']=json.loads(row['settings'])
        return row

@router.put('/profiles/current')
def update(request: Request,body: dict):
    with db(request.app) as c:
        settings=json.loads(one(c,'SELECT settings FROM profiles WHERE id=:active_profile')['settings'])
        settings.update(body.get('settings',{}))
        # Credentials have a separate write-only API and never enter public settings.
        settings={k:v for k,v in settings.items() if 'key' not in k.lower() and 'secret' not in k.lower()}
        execute(c,'UPDATE profiles SET settings=:s WHERE id=:active_profile',s=json.dumps(settings))
        return {'id':active_profile.get(),'settings':settings}
