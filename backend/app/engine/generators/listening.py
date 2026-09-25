from app.engine.generators.base import BaseGenerator


class Generator(BaseGenerator):
    def generate(self, source, direction, fingerprint, candidates):
        target,lang,_rng,p=self.context(source,direction,fingerprint)
        p.update(audio_text=source[lang],audio_lang=lang,mode="typed",answer=source[target],lang=target)
        return self.validate(p)
