from typing import List as TypingList
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.db.models.list import List
from app.schemas.list import ListCreate, ListUpdate


class CRUDList(CRUDBase[List, ListCreate, ListUpdate]):
    async def get_by_board(
            self, db: AsyncSession, *, board_id: int
    ) -> TypingList[List]:
        result = await db.execute(
            select(List)
            .filter(List.board_id == board_id)
            .order_by(List.position)
        )
        return result.scalars().all()

    async def get_with_tasks(self, db: AsyncSession, *, id: int) -> List:
        result = await db.execute(
            select(List)
            .options(selectinload(List.tasks))
            .filter(List.id == id)
        )
        return result.scalars().first()


list_crud = CRUDList(List)
