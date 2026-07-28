from fastapi import APIRouter

from api.routes import worlds, documents, tasks, evaluation_runs, experiments, models, prompt_templates

router = APIRouter(prefix="/api/v1")

router.include_router(worlds.router)
router.include_router(documents.router)
router.include_router(tasks.router)
router.include_router(evaluation_runs.router)
router.include_router(experiments.router)
router.include_router(models.router)
router.include_router(prompt_templates.router)
