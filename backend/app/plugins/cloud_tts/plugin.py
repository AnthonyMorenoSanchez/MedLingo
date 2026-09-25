import hashlib
import importlib
import sqlite3

from fastapi.staticfiles import StaticFiles

from app.config import ROOT
from app.plugins.base import Plugin


class CloudTTS(Plugin):
    id="cloud_tts"
    def configure(self,settings):
        super().configure(settings)
        provider=settings.get("provider","google")
        if provider not in ("google","azure","elevenlabs"):raise ValueError("Unknown speech provider")
        self.provider=importlib.import_module(f"app.plugins.cloud_tts.providers.{provider}").Provider()
        self.cache=ROOT/settings.get("cache_dir","data/audio_cache")
        self.cache.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.cache/"index.sqlite") as c:c.execute("CREATE TABLE IF NOT EXISTS audio_cache(text_hash TEXT PRIMARY KEY,provider TEXT,voice TEXT,path TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    def register_routes(self,app):app.mount("/api/plugins/cloud_tts/audio",StaticFiles(directory=self.cache),name="tts_audio")
    def register_tts_providers(self):return [type(self.provider)]
    async def synthesize(self,body):
        text=body.get("text","")
        if not isinstance(text,str) or not 1<=len(text)<=2000:raise ValueError("Invalid text length")
        lang=body.get("lang","es");voice=self.settings.get("voice","")
        key=hashlib.sha1(f"{self.settings['provider']}|{voice}|{lang}|{text}".encode()).hexdigest()
        dest=self.cache/(key+".mp3")
        if not dest.exists():
            data=await self.provider.synthesize(text,lang,voice)
            dest.write_bytes(data)
            with sqlite3.connect(self.cache/"index.sqlite") as c:c.execute("INSERT OR REPLACE INTO audio_cache(text_hash,provider,voice,path) VALUES(?,?,?,?)",(key,self.settings["provider"],voice,str(dest)))
        return {"url":f"/api/plugins/cloud_tts/audio/{key}.mp3"}
PLUGIN=CloudTTS()
