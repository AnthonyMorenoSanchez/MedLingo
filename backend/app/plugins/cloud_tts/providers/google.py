import base64
import os

import httpx

from app.plugins.cloud_tts.providers.base import TTSProviderBase


class Provider(TTSProviderBase):
    async def synthesize(self,text,lang,voice):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post("https://texttospeech.googleapis.com/v1/text:synthesize",params={"key":os.getenv("GOOGLE_TTS_API_KEY","")},json={"input":{"text":text},"voice":{"languageCode":"es-US" if lang=="es" else "en-US","name":voice},"audioConfig":{"audioEncoding":"MP3"}})
            r.raise_for_status();return base64.b64decode(r.json()["audioContent"])
