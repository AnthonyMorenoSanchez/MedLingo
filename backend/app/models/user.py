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
Profile = type("Profile", (), {})
mapper_registry.map_imperatively(Profile, metadata.tables["profiles"])
QuestionItem = type("QuestionItem", (), {})
mapper_registry.map_imperatively(QuestionItem, metadata.tables["question_items"])
ItemStat = type("ItemStat", (), {})
mapper_registry.map_imperatively(ItemStat, metadata.tables["item_stats"])
Attempt = type("Attempt", (), {})
mapper_registry.map_imperatively(Attempt, metadata.tables["attempts"])
Session = type("Session", (), {})
mapper_registry.map_imperatively(Session, metadata.tables["sessions"])
RuntimeLog = type("RuntimeLog", (), {})
mapper_registry.map_imperatively(RuntimeLog, metadata.tables["runtime_log"])
Bank = type("Bank", (), {})
mapper_registry.map_imperatively(Bank, metadata.tables["banks"])
