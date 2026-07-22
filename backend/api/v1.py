from fastapi import APIRouter

from api.routes import worlds

router = APIRouter(prefix="/api/v1")

router.include_router(worlds.router)
