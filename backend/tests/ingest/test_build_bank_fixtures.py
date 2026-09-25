import sqlite3

import pytest

from ingest.build_bank import build, stable_id, validate_encounter
from ingest.sources.base import RawTerm


def test_offline(tmp_path):
    p=tmp_path/'seed.sqlite'
    first=build(p,True)
    assert first['pass'],first
    assert first['terms']>=2500 and first['sentences']>=1500
    assert p.with_name('bank_report.md').exists()
    with sqlite3.connect(p) as c:ids=c.execute('SELECT id FROM terms ORDER BY id LIMIT 10').fetchall()
    build(p,True)
    with sqlite3.connect(p) as c:assert ids==c.execute('SELECT id FROM terms ORDER BY id LIMIT 10').fetchall()
    assert stable_id('x')==stable_id('x')
    assert RawTerm('kidney','riñón','curated').dict()['en']=='kidney'
@pytest.mark.parametrize('graph',[
 {'start':'a','nodes':[{'id':'a','terminal':True},{'id':'a','terminal':True}]},
 {'start':'a','nodes':[{'id':'a','options':[{'correct':True,'next':'a'}]}]},
 {'start':'a','nodes':[{'id':'a','options':[{'correct':True,'next':'missing'}]}]},
 {'start':'a','nodes':[{'id':'a','options':[]}]},
 {'start':'a','nodes':[{'id':'a','terminal':True},{'id':'b','terminal':True}]},
])
def test_invalid_graphs(graph):
    with pytest.raises(ValueError):validate_encounter(graph)
