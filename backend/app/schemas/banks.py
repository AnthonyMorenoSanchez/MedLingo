from typing import Literal

from pydantic import BaseModel, Field


class BankRule(BaseModel):
    specialties: list[str] = Field(default_factory=list)
    kinds: list[str] = Field(default_factory=list)
    direction: Literal["en2es","es2en"] | None = None
    result_filter: Literal["wrong_only","correct_only","leech","any"] = "any"
    min_wrong: int | None = Field(default=None,ge=0)
    max_ease: float | None = Field(default=None,ge=1.3)
    seen_within_days: int | None = Field(default=None,ge=0)
    limit: int = Field(default=40,ge=1,le=200)
    item_ids: list[int] = Field(default_factory=list)
class BankInput(BaseModel):
    name: str = Field(min_length=1,max_length=120)
    rule: BankRule
