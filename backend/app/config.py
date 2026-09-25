from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MEDLINGO_", env_file=ROOT / ".env", extra="ignore")
    host: str = "127.0.0.1"
    port: int = 8000
    seed_db: str = str(ROOT / "data/seed.sqlite")
    user_db: str = str(ROOT / "data/user.sqlite")
    heartbeat_seconds: float = 30
    log_level: str = "info"
    def path(self, name: str) -> Path:
        p = Path(getattr(self, name))
        return p if p.is_absolute() else ROOT / p
