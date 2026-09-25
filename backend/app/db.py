from contextlib import contextmanager
from contextvars import ContextVar

active_profile: ContextVar[int] = ContextVar("active_profile", default=1)
from pathlib import Path

from sqlalchemy import create_engine, event, text


def engine(path: Path, readonly=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///file:{path}?mode=ro&uri=true" if readonly else f"sqlite:///{path}"
    eng = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})
    @event.listens_for(eng, "connect")
    def pragmas(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        if not readonly:
            conn.execute("PRAGMA journal_mode=WAL")
    return eng

def rows(conn, query, **args):
    return [dict(r) for r in conn.execute(text(query), {"active_profile": active_profile.get(), **args}).mappings()]

def one(conn, query, **args):
    return next(iter(rows(conn, query, **args)), None)

def execute(conn, query, **args):
    return conn.execute(text(query), {"active_profile": active_profile.get(), **args})

@contextmanager
def db(app, seed=False):
    with (app.state.seed if seed else app.state.user).begin() as conn:
        yield conn
