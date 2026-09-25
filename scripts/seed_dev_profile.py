"""Create demo attempts only when explicitly run against a selected demo database."""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.main import create_app
from fastapi.testclient import TestClient
from datetime import date
if 'MEDLINGO_USER_DB' not in os.environ:raise SystemExit('Set MEDLINGO_USER_DB to a demo database first.')
with TestClient(create_app()) as client:
    b=client.post('/api/sessions',json={'count':15}).json()
    for i,item in enumerate(b['items']):
        p=item['payload'];answer=p.get('answer_id',p.get('correct_id',p['giveup']['answer_display']))
        client.post('/api/attempts',json={'session_id':b['session']['id'],'item_id':item['id'],'answer_given':answer if i%4 else 'not the answer','time_ms':8000+i*2000,'client_day':date.today().isoformat()})
    client.post(f"/api/sessions/{b['session']['id']}/end")
