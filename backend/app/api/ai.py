import json
import re
from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.db import db, execute, one, rows
from app.engine.scheduler import now
from app.services import ai
from app.services.hardware import detect

router=APIRouter(prefix='/ai')
class ConfigInput(BaseModel):
    provider: Literal['ollama','openai','anthropic','gemini','groq','mistral','openrouter','compatible']
    base_url: str=Field(max_length=500)
    model: str=Field(max_length=150)
    api_key: str|None=Field(default=None,max_length=1000)

@router.get('/settings')
def settings(request: Request):
    cfg=ai.config(request.app)
    return {**{k:v for k,v in cfg.items() if k!='api_key'},'has_key':bool(cfg.get('api_key')),'providers':ai.PROVIDERS}

@router.put('/settings')
def save(request: Request,body: ConfigInput):
    old=ai.config(request.app);cfg=body.model_dump()
    cfg['base_url']=ai.validate_url(body.base_url)
    cfg['api_key']=body.api_key if body.api_key is not None else old.get('api_key','') if old['provider']==body.provider and old['base_url']==cfg['base_url'] else ''
    ai.save_config(request.app,cfg)
    return {'saved':True}

@router.post('/test')
async def test(request: Request):
    reply=await ai.chat(ai.config(request.app),[{'role':'user','content':'Respond with just: Connected / Conectado.'}])
    return {'reply':reply}

@router.get('/hardware')
def hardware():
    return detect()

@router.get('/models')
async def models(request: Request):
    cfg=ai.config(request.app)
    if cfg['provider']!='ollama':
        return {'models':[]}
    try:
        async with httpx.AsyncClient(timeout=8,trust_env=False) as client:
            r=await client.get(ai.validate_url(cfg['base_url'])+'/api/tags');r.raise_for_status()
        return {'models':[m['name'] for m in r.json()['models']]}
    except (httpx.HTTPError,KeyError,ValueError) as exc:
        raise HTTPException(502,'Ollama is not reachable. Run the Ollama setup script, or check its base URL.') from exc

class PullInput(BaseModel):
    model: str=Field(pattern=r'^[a-zA-Z0-9_.:/-]{1,100}$')

@router.post('/pull')
async def pull(request: Request,body: PullInput):
    cfg=ai.config(request.app)
    if cfg['provider']!='ollama':
        raise HTTPException(409,'Select Ollama first.')
    try:
        async with httpx.AsyncClient(timeout=1800,trust_env=False) as client:
            r=await client.post(ai.validate_url(cfg['base_url'])+'/api/pull',json={'model':body.model,'stream':False});r.raise_for_status()
        if r.json().get('error'):
            raise ValueError()
        cfg['model']=body.model;ai.save_config(request.app,cfg)
        return {'downloaded':True,'model':body.model}
    except (httpx.HTTPError,ValueError) as exc:
        raise HTTPException(502,'Model download failed. Check Ollama, free disk space, and internet access.') from exc

class Start(BaseModel):
    mode: Literal['conversation','clinical']='conversation'
    scenario: str=Field(default='A patient visits a clinic with a headache.',min_length=1,max_length=1500)
class Turn(BaseModel):
    text: str=Field(default='',max_length=4000)
    end: bool=False

def owned(c,cid):
    row=one(c,'SELECT * FROM ai_conversations WHERE id=:id AND profile_id=:active_profile',id=cid)
    if not row:
        raise HTTPException(404,'Conversation not found')
    return row

def public(row):
    return {**row,'messages':json.loads(row['messages'])}

@router.get('/conversations')
def history(request: Request):
    with db(request.app) as c:
        return rows(c,'SELECT id,mode,scenario,ended,created_at FROM ai_conversations WHERE profile_id=:active_profile ORDER BY id DESC LIMIT 50')

@router.get('/conversations/{cid}')
def get_conversation(request: Request,cid: int):
    with db(request.app) as c:
        return public(owned(c,cid))

@router.post('/conversations')
async def start(request: Request,body: Start):
    system='You are a Spanish language practice partner. All cases are fictional educational simulations. '
    if body.mode=='clinical':
        system+='Act as a Spanish-speaking patient. Respond naturally to each learner question, reveal case details gradually, and stay consistent. Do not coach or grade until the encounter ends. '
    else:
        system+='Converse in Spanish. After each learner response, give a brief English correction if needed and ask a follow-up question in Spanish. '
    system+='Scenario: '+body.scenario
    messages=[{'role':'system','content':system},{'role':'user','content':'Begin the conversation with a short Spanish greeting in character.'}]
    reply=await ai.chat(ai.config(request.app),messages)
    # Keep the setup instruction out of the learner transcript and final grading.
    messages=[messages[0],{'role':'assistant','content':reply}]
    with db(request.app) as c:
        cid=execute(c,'INSERT INTO ai_conversations(profile_id,mode,scenario,messages,created_at) VALUES(:active_profile,:m,:s,:v,:t)',m=body.mode,s=body.scenario,v=json.dumps(messages),t=now()).lastrowid
        return public(owned(c,cid))

@router.post('/conversations/{cid}/turn')
async def turn(request: Request,cid: int,body: Turn):
    with db(request.app) as c:
        row=owned(c,cid)
    if row['ended']:
        raise HTTPException(409,'This conversation has ended. Start a new one.')
    messages=json.loads(row['messages'])
    if not body.end and not body.text.strip():
        raise HTTPException(422,'Enter a response first.')
    if sum(m['role']=='user' for m in messages)>=20 and not body.end:
        raise HTTPException(409,'This encounter has reached 20 responses. End it to receive feedback.')
    if body.text.strip():
        messages.append({'role':'user','content':body.text.strip()})
    prompt=messages[:]
    if body.end:
        prompt.append({'role':'user','content':'End the simulation. Evaluate ONLY the learner user messages above. Give an overall language-practice score out of 100, and four scores out of 25: Spanish clarity/grammar, medical vocabulary, empathy/register, and relevant information gathering. Cite concrete examples, corrections, strengths, missed questions, and next practice steps. If no learner answers exist, say not enough evidence and do not assign a score. This is formative language feedback, not clinical certification. Respond in English with corrected Spanish examples.'})
    reply=await ai.chat(ai.config(request.app),prompt)
    messages.append({'role':'assistant','content':reply})
    with db(request.app) as c:
        result=execute(c,'UPDATE ai_conversations SET messages=:m,ended=:e WHERE id=:id AND profile_id=:active_profile AND messages=:old AND ended=0',m=json.dumps(messages),e=int(body.end),id=cid,old=row['messages'])
        if not result.rowcount:
            raise HTTPException(409,'Another response was saved first. Reload the conversation.')
        return public(owned(c,cid))

class Generate(BaseModel):
    specialty: str=Field(max_length=100)
    count: int=Field(default=10,ge=1,le=20)

@router.post('/generate')
async def generate(request: Request,body: Generate):
    with db(request.app,True) as seed:
        if not one(seed,'SELECT id FROM specialties WHERE id=:s',s=body.specialty):
            raise HTTPException(422,'Unknown specialty')
        existing=rows(seed,'SELECT en,es FROM sentences')+rows(seed,'SELECT en,es FROM terms')
    with db(request.app) as c:
        existing+=rows(c,'SELECT en,es FROM generated_content WHERE profile_id=:active_profile')
    seen_en={r['en'].strip().casefold() for r in existing};seen_es={r['es'].strip().casefold() for r in existing}
    reply=await ai.chat(ai.config(request.app),[{'role':'system','content':'Generate bilingual language-learning examples, not patient-specific medical advice. Return only a JSON array of objects with en and es strings. Each pair must be an accurate natural translation, 5–18 words long. Avoid prescribing treatment or dosages.'},{'role':'user','content':f'Create {body.count} varied, distinct {body.specialty} clinic conversation sentences. Use a new combination of contexts and wording.'}])
    try:
        cleaned=re.sub(r'^```(?:json)?\s*|\s*```$','',reply.strip())
        data=json.loads(cleaned)
        if not isinstance(data,list):
            raise TypeError()
        validated=[]
        for r in data[:body.count]:
            if not isinstance(r,dict) or not all(isinstance(r.get(k),str) and 5<=len(r[k])<=500 for k in ('en','es')):
                raise ValueError()
            en=r['en'].strip();es=r['es'].strip()
            if en.casefold() in seen_en or es.casefold() in seen_es:
                continue
            seen_en.add(en.casefold());seen_es.add(es.casefold());validated.append((en,es))
    except (ValueError,TypeError) as exc:
        raise HTTPException(502,'Model output was not valid bilingual JSON. No material was saved; try another model.') from exc
    added=0
    with db(request.app) as c:
        for en,es in validated:
            added+=execute(c,'INSERT OR IGNORE INTO generated_content(profile_id,en,es,specialty_id) VALUES(:active_profile,:en,:es,:s)',en=en,es=es,s=body.specialty).rowcount
    return {'added':added,'note':'AI-generated language practice; translations may need correction.'}
