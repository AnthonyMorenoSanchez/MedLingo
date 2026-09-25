from abc import ABC


class Plugin(ABC):
    id: str
    version="0.1.0"
    def configure(self,settings):self.settings=settings
    def register_routes(self,app):return None
    def register_question_types(self):return {}
    def register_data_sources(self):return []
    def register_tts_providers(self):return []
    def frontend_manifest(self):return {"modules":[],"widgets":[],"questionTypes":[]}
