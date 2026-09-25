from tests.conftest import attempt, session


def test_wrong_hint_and_duplicate(client):
    b=session(client,count=2);item=b['items'][0]
    r=client.post(f"/api/items/{item['id']}/hint?session_id={b['session']['id']}&level=1")
    assert r.status_code==200 and r.json()['text']
    result=attempt(client,b,item,gave=True,hint=True).json()
    assert result['stats_after']['wrong_count']==1
    assert result['stats_after']['gave_up_count']==1
    assert result['stats_after']['hint_count']==1
    assert attempt(client,b,item).status_code==409
    other=session(client,count=1,direction='es2en')
    assert attempt(client,other,b['items'][1]).status_code==400
    test=session(client,mode='wrong_test',count=20)
    assert test['session']['planned_count']==1
    assert client.post(f"/api/items/{item['id']}/hint?session_id={test['session']['id']}").status_code==403
    assert attempt(client,test,test['items'][0],hint=True).status_code==400

def test_accents(client):
    b=session(client,count=1,kinds=['fill_blank'])
    from app.engine.normalize import normalize
    p=b['items'][0]['payload']
    r=attempt(client,b,b['items'][0],answer=normalize(p['giveup']['answer_display'],accents=True))
    assert r.json()['result']=='correct'
