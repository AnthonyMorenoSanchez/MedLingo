from fastapi import APIRouter

from app.api import (
    attempts,
    banks,
    encounters,
    health,
    profiles,
    questions,
    runtime,
    sessions,
    specialties,
    stats,
    terms,
    tts,
)

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(terms.router)
router.include_router(specialties.router)
router.include_router(questions.router)
router.include_router(attempts.router)
router.include_router(sessions.router)
router.include_router(stats.router)
router.include_router(banks.router)
router.include_router(encounters.router)
router.include_router(tts.router)
router.include_router(runtime.router)
router.include_router(profiles.router)

from app.api import ai

router.include_router(ai.router)
from app.api import voice

router.include_router(voice.router)
