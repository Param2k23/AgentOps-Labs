import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.prompt_template import PromptTemplateRepository
from schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)

router = APIRouter(prefix="/prompt-templates", tags=["Prompt Templates"])


@router.post("", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(
    payload: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    repo = PromptTemplateRepository(db)
    template = await repo.create(
        name=payload.name,
        user_prompt_template=payload.user_prompt_template,
        description=payload.description,
        system_prompt=payload.system_prompt,
        version=payload.version,
        is_default=payload.is_default
    )
    return template


@router.get("", response_model=List[PromptTemplateResponse])
async def list_prompt_templates(db: Session = Depends(get_db)):
    repo = PromptTemplateRepository(db)
    templates = await repo.get_all()
    return templates


@router.get("/{template_id}", response_model=PromptTemplateResponse)
async def get_prompt_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    repo = PromptTemplateRepository(db)
    template = await repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt Template not found")
    return template


@router.put("/{template_id}", response_model=PromptTemplateResponse)
async def update_prompt_template(
    template_id: uuid.UUID,
    payload: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):
    repo = PromptTemplateRepository(db)
    update_data = payload.model_dump(exclude_unset=True)
    template = await repo.update(template_id, **update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt Template not found")
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    repo = PromptTemplateRepository(db)
    success = await repo.delete(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt Template not found")
