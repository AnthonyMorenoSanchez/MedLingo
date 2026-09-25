from typing import Any, Literal

from pydantic import BaseModel, Field

Kind = Literal['mcq','fill_blank','drag_slot','drag_order','listening','encounter']
class Hint(BaseModel):
    type: str
    value: str
class GiveUp(BaseModel):
    answer_display: str
    explanation_en: str
    explanation_es: str
    regional_notes: list[dict] = Field(default_factory=list)
class Payload(BaseModel):
    model_config = {'extra':'allow'}
    hint: dict
    giveup: dict
class Option(BaseModel):
    id: str
    text: str
class McqPayload(Payload):
    prompt: str
    prompt_lang: Literal['en','es']
    options: list[Option] = Field(min_length=4,max_length=4)
    answer_id: str
    audio_text: str
    audio_lang: Literal['en','es']
    explanation: str
class Blank(BaseModel):
    start: int
    end: int
    answer: str
    accepted: list[str]
class FillBlankPayload(Payload):
    sentence_masked: str
    sentence_full: str
    blank: Blank
    lang: Literal['en','es']
    audio_text: str
    hint_seed: str
class DragSlotPayload(Payload):
    sentence_masked: str
    blanks: list[dict] = Field(min_length=1)
    tiles: list[Option] = Field(min_length=4)
    lang: Literal['en','es']
class DragOrderPayload(Payload):
    target_sentence: str
    tiles: list[Option] = Field(min_length=1)
    distractor_tile_ids: list[str]
    lang: Literal['en','es']
    audio_text: str
class ListeningPayload(Payload):
    audio_text: str
    audio_lang: Literal['en','es']
    mode: Literal['mcq','typed']
    answer: str
class EncounterPayload(Payload):
    encounter_id: str
    node_id: str
    patient_line_es: str
    patient_line_en: str
    options: list[dict]
    correct_id: str
    feedback: dict[str,str]
PAYLOADS: dict[str,type[Payload]]={'mcq':McqPayload,'fill_blank':FillBlankPayload,'drag_slot':DragSlotPayload,'drag_order':DragOrderPayload,'listening':ListeningPayload,'encounter':EncounterPayload}
class Question(BaseModel):
    id: int
    kind: str
    direction: str
    specialty_id: str
    payload: dict[str,Any]
class SessionInput(BaseModel):
    mode: Literal['learn','review','wrong_test','correct_drill','bank','encounter']='learn'
    direction: Literal['en2es','es2en']='en2es'
    specialties: list[str]=Field(default_factory=list)
    kinds: list[Kind]=Field(default=['mcq','fill_blank','drag_slot','drag_order','listening'])
    difficulty_min: int=Field(default=1,ge=1,le=5)
    difficulty_max: int=Field(default=5,ge=1,le=5)
    count: int=Field(default=15,ge=1,le=200)
    test_mode: bool=False
    review_encounter: bool=False
    bank_id: int | None=None
    encounter_id: str | None=None
    item_ids: list[int]=Field(default_factory=list)
class SessionBatch(BaseModel):
    session: dict
    items: list[Question]
