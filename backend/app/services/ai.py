"""Small HTTP adapters; secrets stay on the local backend."""
import json
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from app.db import db, execute, one

PROVIDERS = {
    'ollama': 'http://127.0.0.1:11434',
    'openai': 'https://api.openai.com/v1',
    'anthropic': 'https://api.anthropic.com/v1',
    'gemini': 'https://generativelanguage.googleapis.com/v1beta/openai',
    'groq': 'https://api.groq.com/openai/v1',
    'mistral': 'https://api.mistral.ai/v1',
    'openrouter': 'https://openrouter.ai/api/v1',
    'compatible': 'http://127.0.0.1:1234/v1',
}

def config(app):
    with db(app) as c:
        row=one(c,'SELECT config FROM ai_settings WHERE profile_id=:active_profile')
    return json.loads(row['config']) if row else {'provider':'ollama','base_url':PROVIDERS['ollama'],'model':'','api_key':''}

def save_config(app, value):
    with db(app) as c:
        execute(c,'INSERT INTO ai_settings VALUES(:active_profile,:v) ON CONFLICT(profile_id) DO UPDATE SET config=:v',v=json.dumps(value))

def validate_url(url):
    p=urlparse(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise HTTPException(422,'Use an HTTP(S) base URL without credentials or query parameters.')
    if p.scheme=='http' and p.hostname not in ('localhost','127.0.0.1','::1'):
        # Local LAN endpoints are intentional for WSL/desktop model servers.
        import ipaddress
        try:
            if not ipaddress.ip_address(p.hostname).is_private:
                raise ValueError()
        except ValueError:
            raise HTTPException(422,'Remote providers require HTTPS; HTTP is allowed for local IP addresses only.')
    return url.rstrip('/')

async def chat(cfg, messages):
    provider=cfg['provider']; base=validate_url(cfg['base_url'])
    if not cfg.get('model'):
        raise HTTPException(409,'Choose a model in AI settings first.')
    headers={}
    if provider not in ('ollama','compatible') and not cfg.get('api_key'):
        raise HTTPException(409,'Add your API key in AI settings first.')
    if provider=='ollama':
        endpoint='/api/chat'
        payload={'model':cfg['model'],'messages':messages,'stream':False,'options':{'num_ctx':4096,'num_predict':900}}
        if cfg['model'].startswith('qwen3'):
            payload['think']=False
    elif provider=='anthropic':
        endpoint='/messages'
        headers={'x-api-key':cfg['api_key'],'anthropic-version':'2023-06-01'}
        payload={'model':cfg['model'],'max_tokens':1200,'system':'\n'.join(m['content'] for m in messages if m['role']=='system'),'messages':[m for m in messages if m['role']!='system']}
    else:
        endpoint='/chat/completions'
        if cfg.get('api_key'):
            headers={'Authorization':'Bearer '+cfg['api_key']}
        payload={'model':cfg['model'],'messages':messages}
    try:
        async with httpx.AsyncClient(timeout=180,trust_env=False) as client:
            response=await client.post(base+endpoint,headers=headers,json=payload)
            response.raise_for_status()
        data=response.json()
        if provider=='ollama':
            result=data['message']['content']
        elif provider=='anthropic':
            result='\n'.join(x['text'] for x in data['content'] if x.get('type')=='text')
        else:
            result=data['choices'][0]['message']['content']
        if not isinstance(result,str) or not result.strip():
            raise ValueError('Empty response')
        return result
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502,f'Model provider returned HTTP {exc.response.status_code}. Check the model name, key, quota, and endpoint.') from exc
    except (httpx.HTTPError,KeyError,ValueError,TypeError) as exc:
        raise HTTPException(502,'The model did not respond correctly. Check that it is running and the endpoint is reachable.') from exc
