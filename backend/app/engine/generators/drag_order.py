from app.engine.generators.base import BaseGenerator


class Generator(BaseGenerator):
    def generate(self, source, direction, fingerprint, candidates):
        target,lang,rng,p=self.context(source,direction,fingerprint)
        tiles=[{"id":str(i),"text":v} for i,v in enumerate(source[target].split())]
        distractors=[{"id":"d0","text":"ayer" if target=="es" else "yesterday"},{"id":"d1","text":"mañana" if target=="es" else "tomorrow"}]
        tiles+=distractors
        rng.shuffle(tiles)
        p.update(prompt=source[lang],prompt_lang=lang,target_sentence=source[target],tiles=tiles,distractor_tile_ids=["d0","d1"],lang=target)
        return self.validate(p)
