from typing import List as TypingList

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.db.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def get_by_list(self, db: AsyncSession, *, list_id: int) -> TypingList[Task]:
        result = await db.execute(
            select(Task)
            .filter(Task.list_id == list_id)
            .order_by(Task.position)
        )
        return result.scalars().all()

    async def move_to_list(
            self, db: AsyncSession, *, task: Task, list_id: int, position: int = None
    ) -> Task:
        task.list_id = list_id
        if position is not None:
            task.position = position
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task


task = CRUDTask(Task)
