from fastapi import APIRouter

from api.routes import worlds, documents

router = APIRouter(prefix="/api/v1")

router.include_router(worlds.router)
router.include_router(documents.router)
