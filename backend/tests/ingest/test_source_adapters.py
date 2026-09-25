import json

import httpx

from ingest import fetch
from ingest.sources import decs, wikidata, wiktionary


def test_parsers_on_minimal_format_examples(tmp_path,monkeypatch):
    # Synthetic parser inputs are confined to tests, never shipped as source snapshots.
    monkeypatch.setattr(decs,'FIXTURES',tmp_path)
    (tmp_path/'decs_sample.xml').write_text('<records><record id="test"><en>kidney</en><es>riñón</es><tree>A05</tree></record></records>')
    assert next(iter(decs.DeCS().terms()))['es']=='riñón'
    monkeypatch.setattr(wiktionary,'FIXTURES',tmp_path)
    (tmp_path/'wiktionary_sample.json').write_text('{"riñón":{"gender_es":"m"}}')
    assert next(iter(wiktionary.enrich([{'es':'riñón'}])))['gender_es']=='m'
    monkeypatch.setattr(wikidata,'FIXTURES',tmp_path)
    (tmp_path/'wikidata_test.json').write_text(json.dumps({'results':{'bindings':[{'en':{'value':'kidney'}}]}}))
    assert list(wikidata.Wikidata().terms())==[]

def test_refresh_failure_preserves_snapshots(tmp_path,monkeypatch):
    monkeypatch.setattr(fetch,'FIXTURES',tmp_path)
    monkeypatch.setattr(fetch.time,'sleep',lambda _:None)
    p=tmp_path/'wikidata_disease.json';p.write_text('original snapshot')
    def get(self,url,**kwargs):raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx.Client,'get',get)
    fetch.refresh()
    assert p.read_text()=='original snapshot'
    assert 'fixture fallback' in (tmp_path/'fetch_log.json').read_text()

def test_refresh_success(tmp_path,monkeypatch):
    monkeypatch.setattr(fetch,'FIXTURES',tmp_path)
    def get(self,url,**kwargs):
        req=httpx.Request('GET',url)
        if 'medlineplus' in url:return httpx.Response(200,content=b'<health-topics/>',request=req)
        return httpx.Response(200,json={'results':{'bindings':[{'en':{'value':'kidney'},'es':{'value':'riñón'}}]}},request=req)
    monkeypatch.setattr(httpx.Client,'get',get)
    fetch.refresh()
    assert (tmp_path/'medlineplus_sample.xml').exists()
    assert 'fetched' in (tmp_path/'fetch_log.json').read_text()
