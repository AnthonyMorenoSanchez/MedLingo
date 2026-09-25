from datetime import date

from pydantic import BaseModel, Field


class AttemptInput(BaseModel):
    item_id: int
    session_id: int
    answer_given: str = Field(default="",max_length=2000)
    time_ms: int = Field(ge=0,le=86400000)
    hint_used: bool = False
    gave_up: bool = False
    client_day: date
class AttemptResult(BaseModel):
    result: str
    feedback: str
    correct_answer: str
    stats_after: dict
    xp: int
