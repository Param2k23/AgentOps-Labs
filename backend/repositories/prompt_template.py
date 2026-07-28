import uuid
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.prompt_template import PromptTemplate

class PromptTemplateRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get(self, template_id: uuid.UUID) -> Optional[PromptTemplate]:
        stmt = select(PromptTemplate).where(PromptTemplate.id == template_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> List[PromptTemplate]:
        stmt = select(PromptTemplate).order_by(PromptTemplate.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_default(self) -> Optional[PromptTemplate]:
        stmt = select(PromptTemplate).where(PromptTemplate.is_default == True)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(
        self,
        name: str,
        user_prompt_template: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        version: int = 1,
        is_default: bool = False,
    ) -> PromptTemplate:
        # If this is set to default, unset others
        if is_default:
            await self._unset_defaults()
            
        template = PromptTemplate(
            name=name,
            user_prompt_template=user_prompt_template,
            description=description,
            system_prompt=system_prompt,
            version=version,
            is_default=is_default,
        )
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def update(
        self,
        template_id: uuid.UUID,
        **kwargs
    ) -> Optional[PromptTemplate]:
        template = await self.get(template_id)
        if not template:
            return None
            
        # If this is set to default, unset others
        if kwargs.get("is_default", False):
            await self._unset_defaults()

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
                
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def delete(self, template_id: uuid.UUID) -> bool:
        template = await self.get(template_id)
        if not template:
            return False
            
        await self.session.delete(template)
        await self.session.commit()
        return True
        
    async def _unset_defaults(self):
        stmt = update(PromptTemplate).where(PromptTemplate.is_default == True).values(is_default=False)
        await self.session.execute(stmt)
