from tests.conftest import attempt, session


def test_stats(client):
    b=session(client,count=2)
    attempt(client,b,b['items'][0]);attempt(client,b,b['items'][1],gave=True)
    r=client.get('/api/stats/overview?day=2026-09-13').json()
    assert r['attempts']==2 and r['correct']==1 and r['accuracy']==50
    assert r['today_ms']==2400 and r['total_study_ms']>0
    for endpoint in ['/stats/specialties','/stats/time','/stats/wrong_trend','/review?tab=wrong','/review?tab=correct','/review?tab=leech','/terms?q=renal','/specialties','/tts/providers','/plugins']:
        assert client.get('/api'+endpoint).status_code==200
    assert client.get('/api/review?tab=wrong').json()['total']==1
    assert client.get('/api/terms?size=101').status_code==422
    assert client.get('/api/not_real').json()['error']['code']=='404'
