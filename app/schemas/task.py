from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.db.models.task import TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    position: int = Field(default=0, ge=0)


class TaskCreate(TaskBase):
    list_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    position: Optional[int] = Field(None, ge=0)


class TaskMove(BaseModel):
    list_id: int
    position: Optional[int] = Field(None, ge=0)


class TaskResponse(TaskBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

