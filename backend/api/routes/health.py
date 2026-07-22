from fastapi import APIRouter, Depends

from api.dependencies import get_app_settings
from config.settings import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(settings: Settings = Depends(get_app_settings)) -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }
