import shutil

import pytest
from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.main import create_app


@pytest.fixture
def settings(tmp_path):
    seed=tmp_path/"seed.sqlite"
    shutil.copy(ROOT/"data/seed.sqlite",seed)
    return Settings(seed_db=str(seed),user_db=str(tmp_path/"user.sqlite"),heartbeat_seconds=.02)
@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as c:yield c

def session(client,**kwargs):
    r=client.post("/api/sessions",json={"count":10,"specialties":["urology"],**kwargs})
    assert r.status_code==200,r.text
    return r.json()
def attempt(client,batch,item,gave=False,answer=None,hint=False):
    p=item["payload"]
    correct=p.get("answer_id",p.get("correct_id",p["giveup"]["answer_display"]))
    return client.post("/api/attempts",json={"session_id":batch["session"]["id"],"item_id":item["id"],"answer_given":correct if answer is None else answer,"time_ms":1200,"hint_used":hint,"gave_up":gave,"client_day":"2026-09-13"})
