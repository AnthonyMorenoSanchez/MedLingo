import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import execute
from app.main import create_app
from tests.conftest import attempt, session


def test_restart(settings):
    with TestClient(create_app(settings)) as c:
        b=session(c,count=1);attempt(c,b,b['items'][0]);c.post(f"/api/sessions/{b['session']['id']}/end")
        totals=c.get('/api/stats/overview').json()
        time.sleep(.05)
        runtime=c.get('/api/runtime').json()
        with c.app.state.seed.begin() as connection, pytest.raises(OperationalError):
            execute(connection,"DELETE FROM terms")
    with TestClient(create_app(settings)) as c:
        assert c.get('/api/stats/overview').json()['attempts']==totals['attempts']
        assert c.get('/api/stats/overview').json()['total_study_ms']==totals['total_study_ms']
        time.sleep(.03)
        new=c.get('/api/runtime').json()
        assert new['restarts']==runtime['restarts']+1
        assert new['total_runtime_s']>=runtime['total_runtime_s']
