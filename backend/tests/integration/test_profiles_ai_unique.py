import json
import sqlite3

import pytest

from app.services import ai
from app.services.hardware import detect
from tests.conftest import attempt, session


def new_user(client,name='Second learner'):
    r=client.post('/api/profiles',json={'name':name})
    assert r.status_code==200,r.text
    return str(r.json()['id'])


def test_profile_isolation_and_ownership(client):
    first=session(client,count=3)
    attempt(client,first,first['items'][0])
    client.put('/api/profiles/current',json={'settings':{'voice_es':'Spanish voice','daily_goal':25}})
    bank=client.post('/api/banks',json={'name':'Mine','rule':{}}).json()
    second=new_user(client)
    client.headers['X-Profile-ID']=second
    assert client.get('/api/profiles/current').json()['settings']=={}
    assert client.get('/api/stats/overview').json()['attempts']==0
    assert client.get('/api/sessions').json()==[]
    assert client.get('/api/banks').json()==[]
    assert client.get('/api/review?tab=correct').json()['total']==0
    assert client.get('/api/sessions/'+str(first['session']['id'])).status_code==404
    assert client.post('/api/sessions/'+str(first['session']['id'])+'/end').status_code==404
    assert attempt(client,first,first['items'][1]).status_code==404
    assert client.delete('/api/banks/'+str(bank['id'])).status_code==404
    own=session(client,count=2)
    attempt(client,own,own['items'][0])
    assert client.get('/api/stats/overview').json()['attempts']==1
    client.headers['X-Profile-ID']='1'
    assert client.get('/api/profiles/current').json()['settings']['daily_goal']==25
    assert client.get('/api/stats/overview').json()['attempts']==1


def test_profile_validation(client):
    assert client.post('/api/profiles',json={'name':'   '}).status_code==422
    assert client.post('/api/profiles',json={'name':'Default'}).status_code==409
    assert client.get('/api/profiles/current',headers={'X-Profile-ID':'99999'}).status_code==404
    assert client.get('/api/profiles/current',headers={'X-Profile-ID':'1 OR 1=1'}).status_code==400


def test_unique_across_modes_directions_and_sessions(client):
    seen=set()
    for direction in ('en2es','es2en','en2es'):
        batch=session(client,count=30,direction=direction)
        assert len(batch['items'])==20  # paged batch
        items=batch['items']+client.get(f"/api/sessions/{batch['session']['id']}/next?after_item_id={batch['items'][-1]['id']}").json()['items']
        assert len(items)==30
        for item in items:
            p=item['payload']
            texts={p.get('prompt','').casefold(),p['giveup']['answer_display'].casefold(),p.get('audio_text','').casefold()}-{''}
            assert not texts&seen
            seen|=texts
            assert attempt(client,batch,item).status_code==200
    review=session(client,mode='correct_drill',count=5)
    assert all(i['payload']['giveup']['answer_display'].casefold() in seen for i in review['items'])


def test_exhaustion_never_recycles_and_is_per_profile(client,settings):
    with sqlite3.connect(settings.path('seed_db')) as c:
        c.execute('UPDATE terms SET difficulty=5')
        c.execute('UPDATE sentences SET difficulty=5')
        c.execute("UPDATE terms SET difficulty=1 WHERE id=(SELECT term_id FROM term_specialties WHERE specialty_id='urology' LIMIT 1)")
    filters={'specialties':['urology'],'difficulty_min':1,'difficulty_max':1,'count':5}
    batch=client.post('/api/sessions',json=filters).json()
    assert batch['session']['planned_count']==1
    assert attempt(client,batch,batch['items'][0],gave=True).status_code==200
    assert client.post('/api/sessions',json=filters).status_code==409
    reviewed=client.post('/api/sessions',json={**filters,'mode':'review'}).json()
    assert reviewed['items'][0]['id']==batch['items'][0]['id']
    pid=new_user(client)
    assert client.post('/api/sessions',json=filters,headers={'X-Profile-ID':pid}).json()['session']['planned_count']==1


def test_api_key_write_only_and_separate(client):
    cfg={'provider':'openai','model':'test-model','base_url':'https://api.openai.com/v1','api_key':'private-secret'}
    assert client.put('/api/ai/settings',json=cfg).status_code==200
    result=client.get('/api/ai/settings')
    assert 'private-secret' not in result.text and result.json()['has_key']
    assert 'private-secret' not in client.get('/api/profiles/current').text
    cfg.pop('api_key')
    client.put('/api/ai/settings',json=cfg)
    assert client.get('/api/ai/settings').json()['has_key']
    cfg['base_url']='https://other.example/v1'
    client.put('/api/ai/settings',json=cfg)
    assert not client.get('/api/ai/settings').json()['has_key']
    pid=new_user(client)
    assert not client.get('/api/ai/settings',headers={'X-Profile-ID':pid}).json()['has_key']


def test_conversations_persist_and_grade_at_end(client,monkeypatch):
    calls=[]
    async def fake(cfg,messages):
        calls.append(messages)
        return 'Score: 80/100. Grammar: 20/25.' if 'End the simulation' in messages[-1]['content'] else 'Hola. Me duele la cabeza.'
    monkeypatch.setattr(ai,'chat',fake)
    r=client.post('/api/ai/conversations',json={'mode':'clinical','scenario':'Headache'}).json()
    cid=r['id']
    assert 'Do not coach or grade until' in calls[0][0]['content']
    r=client.post(f'/api/ai/conversations/{cid}/turn',json={'text':'¿Desde cuándo?'}).json()
    assert not r['ended'] and r['messages'][-2]['content']=='¿Desde cuándo?'
    r=client.post(f'/api/ai/conversations/{cid}/turn',json={'end':True}).json()
    assert r['ended'] and '80/100' in r['messages'][-1]['content']
    assert client.get(f'/api/ai/conversations/{cid}').json()['ended']
    assert client.post(f'/api/ai/conversations/{cid}/turn',json={'text':'hola'}).status_code==409
    pid=new_user(client)
    assert client.get(f'/api/ai/conversations/{cid}',headers={'X-Profile-ID':pid}).status_code==404
    assert client.get('/api/ai/conversations',headers={'X-Profile-ID':pid}).json()==[]


def test_generated_content_validated_deduped_and_used(client,monkeypatch,settings):
    async def fake(cfg,messages):
        return json.dumps([{'en':'Tell me whether your discomfort worsens after lunch.','es':'Dígame si su molestia empeora después del almuerzo.'}]*2)
    monkeypatch.setattr(ai,'chat',fake)
    r=client.post('/api/ai/generate',json={'specialty':'urology','count':2})
    assert r.json()['added']==1
    assert client.post('/api/ai/generate',json={'specialty':'urology'}).json()['added']==0
    with sqlite3.connect(settings.path('seed_db')) as c:
        c.execute('UPDATE terms SET difficulty=5');c.execute('UPDATE sentences SET difficulty=5')
    r=client.post('/api/sessions',json={'specialties':['urology'],'difficulty_max':2,'kinds':['drag_order']})
    assert r.status_code==200 and r.json()['session']['planned_count']==1
    assert 'Dígame' in r.json()['items'][0]['payload']['target_sentence']
    assert client.post('/api/sessions',json={'specialties':['urology'],'difficulty_max':2}).status_code==409


def test_generation_rejects_malformed_without_partial_save(client,monkeypatch,settings):
    async def fake(cfg,messages):
        return '[{"en":"valid text","es":"texto válido"}, {"en":42}]'
    monkeypatch.setattr(ai,'chat',fake)
    assert client.post('/api/ai/generate',json={'specialty':'urology'}).status_code==502
    with sqlite3.connect(settings.path('user_db')) as c:
        assert c.execute('SELECT count(*) FROM generated_content').fetchone()[0]==0


def test_missing_model_and_speech_language_validation(client):
    assert client.post('/api/ai/test').status_code==409
    r=client.post('/api/voice/speak',json={'text':'Hola','lang':'es','provider':'piper','voice':'en_US-lessac-medium'})
    assert r.status_code==422
    assert client.post('/api/voice/speak',json={'text':'Hola','lang':'es','voice':'../../file'}).status_code==422
    assert client.get('/api/voice/catalog').status_code==200


def test_hardware_recommendation_low_memory(monkeypatch):
    from types import SimpleNamespace

    from app.services import hardware
    monkeypatch.setattr(hardware.psutil,'virtual_memory',lambda:SimpleNamespace(total=16*2**30,available=7*2**30))
    assert detect()['recommended_model']=='qwen3:4b'
    monkeypatch.setattr(hardware.psutil,'virtual_memory',lambda:SimpleNamespace(total=8*2**30,available=4*2**30))
    assert detect()['recommended_model']=='qwen3:1.7b'


@pytest.mark.parametrize('provider',['ollama','anthropic','openai','gemini','groq','mistral','openrouter','compatible'])
@pytest.mark.asyncio
async def test_provider_wire_formats(provider,monkeypatch):
    import httpx
    original=httpx.AsyncClient
    captured=[]
    def handle(request):
        captured.append(request)
        if provider=='ollama':
            data={'message':{'content':'Hola'}}
        elif provider=='anthropic':
            data={'content':[{'type':'text','text':'Hola'}]}
        else:
            data={'choices':[{'message':{'content':'Hola'}}]}
        return httpx.Response(200,json=data)
    monkeypatch.setattr(ai.httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handle),**kw))
    reply=await ai.chat({'provider':provider,'base_url':ai.PROVIDERS[provider],'api_key':'key','model':'qwen3:4b'},[{'role':'system','content':'Teacher'},{'role':'user','content':'Hola'}])
    assert reply=='Hola'
    request=captured[0];body=json.loads(request.content)
    assert body['model']=='qwen3:4b'
    if provider=='anthropic':
        assert request.headers['x-api-key']=='key' and body['system']=='Teacher'
    elif provider=='ollama':
        assert body['stream'] is False and body['think'] is False
    else:
        assert request.headers['authorization']=='Bearer key'
