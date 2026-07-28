import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class PromptTemplateCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: str = Field(..., description="The prompt template string")
    version: int = Field(default=1)
    is_default: bool = Field(default=False)

class PromptTemplateUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    version: Optional[int] = None
    is_default: Optional[bool] = None

class PromptTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    system_prompt: Optional[str]
    user_prompt_template: str
    version: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
