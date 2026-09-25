import pytest

from tests.conftest import attempt, session


@pytest.mark.parametrize('mode',['learn','review','correct_drill','wrong_test'])
def test_modes(client,mode):
    first=session(client,count=4)
    for i,item in enumerate(first['items']):attempt(client,first,item,gave=i%2==0)
    b=session(client,mode=mode,count=6)
    assert b['session']['planned_count']<=6
    if mode=='learn':assert b['session']['planned_count']==6
    elif mode=='review':
        assert b['session']['planned_count']==2
        assert {i['id'] for i in b['items']} <= {i['id'] for i in first['items']}
    else:assert b['session']['planned_count']==2

def test_batch_paging(client):
    b=session(client,count=25)
    assert len(b['items'])==20
    r=client.get(f"/api/sessions/{b['session']['id']}/next?after_item_id={b['items'][-1]['id']}")
    assert len(r.json()['items'])==5
    assert client.get(f"/api/sessions/{b['session']['id']}/next?after_item_id=999999").status_code==400
    assert client.post(f"/api/sessions/{b['session']['id']}/heartbeat").status_code==200
    assert client.get('/api/sessions/999999').status_code==404

def test_resume_excludes_answered(client):
    b=session(client,count=3)
    attempt(client,b,b['items'][0])
    r=client.get(f"/api/sessions/{b['session']['id']}/next").json()
    assert r['session']['completed_count']==1 and len(r['items'])==2
    assert r['items'][0]['id']==b['items'][1]['id']
