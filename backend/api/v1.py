from fastapi import APIRouter

from api.routes import worlds, documents, tasks

router = APIRouter(prefix="/api/v1")

router.include_router(worlds.router)
router.include_router(documents.router)
router.include_router(tasks.router)
