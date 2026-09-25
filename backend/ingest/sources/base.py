from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
@dataclass
class RawTerm:
    en: str
    es: str
    source: str
    semantic_type: str = "other"
    source_id: str = ""
    en_aliases: list = field(default_factory=list)
    es_aliases: list = field(default_factory=list)
    mesh_ids: list = field(default_factory=list)
    icd10_codes: list = field(default_factory=list)
    definition_en: str | None = None
    definition_es: str | None = None
    pos_hint: str = "noun"
    def dict(self):
        return asdict(self)
class BaseSource(ABC):
    @abstractmethod
    def terms(self, offline=True):
        raise NotImplementedError
