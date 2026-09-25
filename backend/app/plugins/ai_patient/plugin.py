import importlib

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.plugins.ai_patient.rubric import score
from app.plugins.base import Plugin


class ChatInput(BaseModel):
    messages:list[dict]=Field(max_length=25)
    end:bool=False
class AIPatient(Plugin):
    id="ai_patient"
    def configure(self,settings):
        super().configure(settings)
        name=settings.get("provider","ollama")
        if name not in ("openai","anthropic","ollama"):raise ValueError("Unknown AI provider")
        self.provider=importlib.import_module(f"app.plugins.ai_patient.providers.{name}").Provider(settings.get("model","llama3.1"))
    def frontend_manifest(self):return {"modules":["ai_patient/ChatPanel"],"widgets":[],"questionTypes":[]}
    def register_routes(self,app):
        router=APIRouter(prefix="/api/plugins/ai_patient")
        @router.post("/chat",response_model=dict)
        async def chat(body:ChatInput):
            messages=[{"role":"system","content":"Play a fictional Spanish-speaking patient in a language-learning exercise. Do not prescribe or give medical advice."},*body.messages]
            finish=body.end or sum(m.get("role")=="user" for m in body.messages)>=self.settings.get("max_turns",12)
            if finish:messages.append({"role":"user","content":"End the simulation. Give concise Spanish grammar and vocabulary corrections only."})
            try:return {"reply":await self.provider.chat(messages),"rubric":score(body.messages) if finish else None,"ended":finish}
            except Exception as e:raise HTTPException(502,"AI provider unavailable. Check configuration and connection.") from e
        app.include_router(router)
PLUGIN=AIPatient()
