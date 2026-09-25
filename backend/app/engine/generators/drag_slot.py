from app.engine.generators.mcq import Generator as Mcq


class Generator(Mcq):
    def generate(self, source, direction, fingerprint, candidates):
        p=super().generate(source,direction,fingerprint,candidates)
        p.update(sentence_masked=("El término es {{1}}." if p["audio_lang"]=="es" else "The term is {{1}}."),blanks=[{"index":1,"answer_tile_id":"0"}],tiles=p.pop("options"),lang=p["audio_lang"])
        return self.validate(p)
