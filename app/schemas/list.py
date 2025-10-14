# app/schemas/list.py
from pydantic import BaseModel, Field
from typing import Optional, List as TypingList, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.task import TaskResponse


class ListBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    position: int = Field(default=0, ge=0)


class ListCreate(ListBase):
    board_id: int


class ListUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[int] = Field(None, ge=0)


class ListResponse(ListBase):
    id: int
    board_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListWithTasks(ListResponse):
    tasks: TypingList["TaskResponse"] = []  # Forward reference como string