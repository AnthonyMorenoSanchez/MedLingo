import os

import httpx

from app.plugins.ai_patient.providers.base import ChatProviderBase


class Provider(ChatProviderBase):
    async def chat(self,messages):
        async with httpx.AsyncClient(timeout=60) as c:
            r=await c.post('https://api.anthropic.com/v1/messages',json={"model":self.model,"system":"You are a simulated Spanish-speaking patient for language practice, not a clinician.","messages":[m for m in messages if m["role"]!="system"],"max_tokens":500},headers={"x-api-key":os.getenv("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01"})
            r.raise_for_status();return r.json()["content"][0]["text"]
