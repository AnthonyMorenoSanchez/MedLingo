import base64
import importlib

import httpx
import pytest
from fastapi import FastAPI

from app.plugins.ai_patient.rubric import score
from app.plugins.loader import load_plugins


@pytest.mark.asyncio
@pytest.mark.parametrize('name',['google','azure','elevenlabs'])
async def test_tts_http(name,monkeypatch):
    monkeypatch.setenv('AZURE_TTS_REGION','eastus')
    async def post(self,url,**kwargs):
        return httpx.Response(200,json={'audioContent':base64.b64encode(b'mp3 bytes').decode()} if name=='google' else None,content=None if name=='google' else b'mp3 bytes',request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx.AsyncClient,'post',post)
    provider=importlib.import_module(f'app.plugins.cloud_tts.providers.{name}').Provider()
    assert await provider.synthesize('riñón','es','voice')==b'mp3 bytes'

@pytest.mark.asyncio
@pytest.mark.parametrize('name',['openai','anthropic','ollama'])
async def test_chat_http(name,monkeypatch):
    response={'openai':{'choices':[{'message':{'content':'Me duele.'}}]},'anthropic':{'content':[{'text':'Me duele.'}]},'ollama':{'message':{'content':'Me duele.'}}}[name]
    async def post(self,url,**kwargs):
        return httpx.Response(200,json=response,request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx.AsyncClient,'post',post)
    provider=importlib.import_module(f'app.plugins.ai_patient.providers.{name}').Provider('test-model')
    assert await provider.chat([{'role':'user','content':'¿Cómo se siente?'}])=='Me duele.'

def test_broken_plugin_isolated(tmp_path):
    p=tmp_path/'plugins.toml';p.write_text('[does_not_exist]\nenabled=true\n')
    assert load_plugins(FastAPI(),p)==[]
    assert score([{'role':'user','content':'Entiendo su dolor, por favor.'}])['empathy_phrases']==2
