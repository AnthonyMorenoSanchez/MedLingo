import os
from xml.sax.saxutils import escape

import httpx

from app.plugins.cloud_tts.providers.base import TTSProviderBase


class Provider(TTSProviderBase):
    async def synthesize(self,text,lang,voice):
        region=os.getenv("AZURE_TTS_REGION","")
        if not region.isalnum():raise ValueError("Set AZURE_TTS_REGION")
        ssml=f'<speak version="1.0" xml:lang="{lang}"><voice name="{escape(voice)}">{escape(text)}</voice></speak>'
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",content=ssml,headers={"Ocp-Apim-Subscription-Key":os.getenv("AZURE_TTS_KEY",""),"Content-Type":"application/ssml+xml","X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3"})
            r.raise_for_status();return r.content
