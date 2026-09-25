import pytest

from tests.conftest import attempt, session


@pytest.mark.parametrize("kind",["mcq","fill_blank","drag_slot","drag_order","listening"])
@pytest.mark.parametrize("direction",["en2es","es2en"])
def test_roundtrip(client,kind,direction):
    b=session(client,kinds=[kind],direction=direction,count=2)
    assert len(b["items"])==2
    for item in b["items"]:
        r=attempt(client,b,item);assert r.status_code==200,r.text;assert r.json()["result"]=="correct"
    result=client.post(f"/api/sessions/{b['session']['id']}/end").json()
    assert result["completed_count"]==2 and result["xp_earned"]==45

def test_bad_filters(client):
    assert client.post('/api/sessions',json={'count':0}).status_code==422
    assert client.post('/api/sessions',json={'kinds':['bogus']}).status_code==422
    assert client.post('/api/sessions',json={'specialties':['missing']}).status_code==409
    assert client.post('/api/sessions',json={'kinds':['encounter']}).status_code==409
