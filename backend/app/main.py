import asyncio
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from alembic import command
from app.api.router import router
from app.config import ROOT, Settings
from app.db import active_profile, engine, execute, one
from app.plugins.loader import load_plugins


def migrate(settings):
    # Alembic connection is injected, so temp databases and normal startup use the same revision.
    cfg=Config(str(ROOT/"backend/alembic.ini"))
    cfg.attributes["database_path"]=settings.path("user_db")
    command.upgrade(cfg,"head")

def create_app(settings=None):
    settings=settings or Settings()
    @asynccontextmanager
    async def lifespan(app):
        if not settings.path("seed_db").exists():
            raise RuntimeError("Seed database missing. Run make ingest-offline first.")
        migrate(settings)
        app.state.settings=settings
        app.state.seed=engine(settings.path("seed_db"),True)
        app.state.user=engine(settings.path("user_db"))
        started=time.monotonic()
        app.state.uptime=lambda:time.monotonic()-started
        stamp=datetime.now(UTC).isoformat()
        with app.state.user.begin() as c:
            execute(c,"INSERT OR IGNORE INTO profiles(id,name,settings,created_at) VALUES(1,'Default','{}',:t)",t=stamp)
            app.state.runtime_id=execute(c,"INSERT INTO runtime_log(process_started_at,last_heartbeat_at) VALUES(:t,:t)",t=stamp).lastrowid
        app.state.plugins=load_plugins(app,ROOT/"plugins.toml")
        def beat(clean=False):
            with app.state.user.begin() as c:
                execute(c,"UPDATE runtime_log SET last_heartbeat_at=:t,ended_cleanly=:clean WHERE id=:id",t=datetime.now(UTC).isoformat(),clean=int(clean),id=app.state.runtime_id)
        async def heartbeat():
            while True:
                await asyncio.sleep(settings.heartbeat_seconds)
                beat()
        task=asyncio.create_task(heartbeat())
        try:yield
        finally:
            task.cancel()
            try:await task
            except asyncio.CancelledError:pass
            beat(True)
            app.state.user.dispose();app.state.seed.dispose()
    app=FastAPI(title="MedLingo",version="0.1.0",lifespan=lifespan)
    @app.middleware("http")
    async def select_profile(request: Request, call_next):
        raw = request.headers.get("X-Profile-ID", "1")
        if not raw.isdigit() or len(raw) > 10:
            return JSONResponse({"error": {"message": "Invalid profile"}}, status_code=400)
        pid = int(raw)
        if request.url.path.startswith("/api/"):
            with app.state.user.connect() as c:
                if not one(c, "SELECT id FROM profiles WHERE id=:p", p=pid):
                    return JSONResponse({"error": {"message": "Profile not found"}}, status_code=404)
        token = active_profile.set(pid)
        try:
            return await call_next(request)
        finally:
            active_profile.reset(token)
    @app.exception_handler(HTTPException)
    async def error(request:Request,exc:HTTPException):
        return JSONResponse({"error":{"code":str(exc.status_code),"message":str(exc.detail)}},status_code=exc.status_code)
    @app.exception_handler(RequestValidationError)
    async def invalid(request:Request,exc:RequestValidationError):
        return JSONResponse({"error":{"code":"validation","message":"Invalid request","details":str(exc)}},status_code=422)
    app.include_router(router)
    dist=ROOT/"frontend/dist"
    if (dist/"assets").exists():app.mount("/assets",StaticFiles(directory=dist/"assets"),name="assets")
    @app.get("/{path:path}",include_in_schema=False)
    def frontend(path:str):
        if path.startswith("api/"):raise HTTPException(404,"API route not found")
        target=(dist/path).resolve()
        if target.is_relative_to(dist.resolve()) and target.is_file():return FileResponse(target)
        if (dist/"index.html").exists():return FileResponse(dist/"index.html")
        return JSONResponse({"message":"Build the frontend with make build."},status_code=503)
    return app
app=create_app()
