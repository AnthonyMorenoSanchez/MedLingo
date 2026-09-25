import os

import httpx

from app.plugins.ai_patient.providers.base import ChatProviderBase


class Provider(ChatProviderBase):
    async def chat(self,messages):
        async with httpx.AsyncClient(timeout=60) as c:
            r=await c.post('https://api.openai.com/v1/chat/completions',json={"model":self.model,"messages":messages},headers={"Authorization":"Bearer "+os.getenv("OPENAI_API_KEY","")})
            r.raise_for_status();return r.json()["choices"][0]["message"]["content"]
