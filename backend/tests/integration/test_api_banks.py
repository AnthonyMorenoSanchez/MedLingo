from tests.conftest import attempt, session


def test_crud(client):
    b=session(client,count=3)
    for item in b['items']:attempt(client,b,item,gave=True)
    rule={'specialties':['urology'],'result_filter':'wrong_only','limit':2}
    count=client.post('/api/banks/preview',json=rule).json()['count']
    bank=client.post('/api/banks',json={'name':'Urology wrong only','rule':rule}).json()
    run=session(client,mode='bank',bank_id=bank['id'],count=10,test_mode=True)
    assert run['session']['mode']=='wrong_test'
    assert client.post(f"/api/items/{run['items'][0]['id']}/hint?session_id={run['session']['id']}").status_code==403
    assert run['session']['planned_count']==count==2
    assert client.get('/api/banks').json()[0]['count']==2
    assert client.delete(f"/api/banks/{bank['id']}").status_code==200
    assert client.post('/api/sessions',json={'mode':'bank','bank_id':bank['id']}).status_code==409
