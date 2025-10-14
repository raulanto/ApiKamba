from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.db.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate


class CRUDBoard(CRUDBase[Board, BoardCreate, BoardUpdate]):
    async def get_by_owner(
            self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Board]:
        result = await db.execute(
            select(Board)
            .filter(Board.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_lists(self, db: AsyncSession, *, id: int) -> Board:
        result = await db.execute(
            select(Board)
            .options(selectinload(Board.lists))
            .filter(Board.id == id)
        )
        return result.scalars().first()

    async def create_with_owner(
            self, db: AsyncSession, *, obj_in: BoardCreate, owner_id: int
    ) -> Board:
        db_obj = Board(
            **obj_in.model_dump(),
            owner_id=owner_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


board = CRUDBoard(Board)

