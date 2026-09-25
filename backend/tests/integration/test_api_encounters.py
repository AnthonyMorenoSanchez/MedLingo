from ingest.build_bank import validate_encounter
from tests.conftest import attempt, session


def test_all_encounters(client):
    encs=client.get('/api/encounters').json()
    assert len(encs)==12
    for enc in encs:
        e=client.get('/api/encounters/'+enc['id']).json();validate_encounter(e['nodes'])
        b=session(client,mode='encounter',encounter_id=enc['id'])
        assert len(b['items'])==6
        for item in b['items']:assert attempt(client,b,item).json()['result']=='correct'
    assert client.post('/api/sessions',json={'mode':'encounter','encounter_id':'missing'}).status_code==409
