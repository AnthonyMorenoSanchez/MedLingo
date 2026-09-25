import os
from urllib.parse import quote

import httpx

from app.plugins.cloud_tts.providers.base import TTSProviderBase


class Provider(TTSProviderBase):
    async def synthesize(self,text,lang,voice):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post("https://api.elevenlabs.io/v1/text-to-speech/"+quote(voice,safe=""),json={"text":text,"model_id":"eleven_multilingual_v2"},headers={"xi-api-key":os.getenv("ELEVENLABS_API_KEY","")})
            r.raise_for_status();return r.content
