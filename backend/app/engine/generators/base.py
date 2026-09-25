import hashlib
import random
from abc import ABC, abstractmethod

from app.schemas.questions import Payload


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, source, direction, fingerprint, candidates):
        raise NotImplementedError
    def context(self, source, direction, fingerprint):
        target = "es" if direction == "en2es" else "en"
        prompt_lang = "en" if target == "es" else "es"
        rng = random.Random(int(hashlib.sha256(fingerprint.encode()).hexdigest(),16))
        answer = source[target]
        common = {"hint":{"type":"letter","value":answer[:1]},"giveup":{"answer_display":answer,"explanation_en":source.get("definition_en") or source["en"],"explanation_es":source.get("definition_es") or source["es"],"regional_notes":source.get("regional_notes",[])},"gender_hint":("la" if source.get("gender_es")=="f" else "el" if source.get("gender_es")=="m" else "el / la" if source.get("gender_es")=="mf" else "This is a phrase."),"alias_hint":next(iter(source.get(target+"_aliases",[])),None),"accepted":source.get(target+"_aliases",[]),"audio_text":answer,"audio_lang":target}
        return target,prompt_lang,rng,common
    def validate(self,payload):
        return Payload.model_validate(payload).model_dump()
