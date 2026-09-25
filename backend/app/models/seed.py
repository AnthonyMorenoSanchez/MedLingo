"""SQLAlchemy mappings, loaded from the canonical schema without opening the user's database."""
import sqlite3
from pathlib import Path

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import registry

_temp = sqlite3.connect(":memory:")
_temp.executescript(Path(__file__).with_suffix(".sql").read_text())
_engine = create_engine("sqlite://", creator=lambda: _temp)
metadata = MetaData()
metadata.reflect(_engine)
mapper_registry = registry(metadata=metadata)
Term = type("Term", (), {})
mapper_registry.map_imperatively(Term, metadata.tables["terms"])
Sentence = type("Sentence", (), {})
mapper_registry.map_imperatively(Sentence, metadata.tables["sentences"])
Template = type("Template", (), {})
mapper_registry.map_imperatively(Template, metadata.tables["templates"])
Specialty = type("Specialty", (), {})
mapper_registry.map_imperatively(Specialty, metadata.tables["specialties"])
Encounter = type("Encounter", (), {})
mapper_registry.map_imperatively(Encounter, metadata.tables["encounters"])
AudioCache = type("AudioCache", (), {})
mapper_registry.map_imperatively(AudioCache, metadata.tables["audio_cache"])
