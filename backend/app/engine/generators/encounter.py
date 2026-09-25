from app.engine.generators.base import BaseGenerator


class Generator(BaseGenerator):
    def generate(self, source, direction, fingerprint, candidates):
        options=source["options"]
        correct=next(o for o in options if o["correct"])
        p={"encounter_id":source["encounter_id"],"node_id":source["id"],"patient_line_es":source["patient_es"],"patient_line_en":source["patient_en"],"options":[{"id":o["id"],"text_es":o["es"],"text_en":o["en"]} for o in options],"correct_id":correct["id"],"feedback":{o["id"]:o["feedback_en"] for o in options},"hint":{"type":"letter","value":correct["es"][:1]},"giveup":{"answer_display":correct["es"],"explanation_en":correct["feedback_en"],"explanation_es":correct["es"],"regional_notes":[]},"audio_text":source["patient_es"],"audio_lang":"es"}
        return self.validate(p)
