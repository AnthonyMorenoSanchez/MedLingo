import os

import httpx

from app.plugins.ai_patient.providers.base import ChatProviderBase


class Provider(ChatProviderBase):
    async def chat(self,messages):
        async with httpx.AsyncClient(timeout=60) as c:
            r=await c.post(os.getenv("OLLAMA_BASE_URL","http://localhost:11434").rstrip("/")+"/api/chat",json={"model":self.model,"messages":messages,"stream":False},headers={})
            r.raise_for_status();return r.json()["message"]["content"]
