from app.engine.distractors import choose
from app.engine.generators.base import BaseGenerator


class Generator(BaseGenerator):
    def generate(self, source, direction, fingerprint, candidates):
        target,lang,rng,p = self.context(source,direction,fingerprint)
        values=[source[target],*choose(source[target],candidates,rng)]
        options=[{"id":str(i),"text":v} for i,v in enumerate(values)]
        rng.shuffle(options)
        p.update(prompt=source[lang],prompt_lang=lang,options=options,answer_id="0",explanation=p["giveup"]["explanation_en"])
        return self.validate(p)
