from app.engine.generators.base import BaseGenerator


class Generator(BaseGenerator):
    def generate(self, source, direction, fingerprint, candidates):
        target,lang,_rng,p = self.context(source,direction,fingerprint)
        p.update(prompt=source[lang],prompt_lang=lang,sentence_masked=("El término es ________." if target=="es" else "The term is ________."),hint_seed=source[target][:1],sentence_full=source[target],blank={"start":0,"end":len(source[target]),"answer":source[target],"accepted":source.get(target+"_aliases",[])},lang=target)
        return self.validate(p)
