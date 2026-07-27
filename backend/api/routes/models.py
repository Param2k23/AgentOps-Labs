from typing import Any, List, Dict
from fastapi import APIRouter

from config.models import MODEL_REGISTRY

router = APIRouter(prefix="/models", tags=["models"])

@router.get("", response_model=List[Dict[str, Any]])
async def get_models() -> Any:
    """Get all enabled models."""
    enabled_models = []
    for model_id, info in MODEL_REGISTRY.items():
        if info.get("enabled"):
            enabled_models.append({
                "id": model_id,
                "display_name": info["display_name"],
                "provider": info["provider"],
                "enabled": info["enabled"],
                "supports_judge": info.get("supports_judge", False)
            })
    return enabled_models
