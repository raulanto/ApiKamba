from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.db.session import get_db
from app.db.models.user import User
from app.schemas import BoardCreate, BoardUpdate, BoardResponse, BoardWithLists

from app.crud.board import board as board_crud

router = APIRouter()


@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
        *,
        db: AsyncSession = Depends(get_db),
        board_in: BoardCreate,
        current_user: User = Depends(get_current_active_user)
) -> BoardResponse:
    """
    Crear un nuevo tablero
    """
    board = await board_crud.create_with_owner(
        db, obj_in=board_in, owner_id=current_user.id
    )
    return board


@router.get("/", response_model=List[BoardResponse])
async def list_boards(
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user: User = Depends(get_current_active_user)
) -> List[BoardResponse]:
    """
    Listar todos los tableros del usuario actual
    """
    boards = await board_crud.get_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return boards


@router.get("/{board_id}", response_model=BoardWithLists)
async def get_board(
        board_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> BoardWithLists:
    """
    Obtener un tablero con todas sus listas
    """
    board = await board_crud.get_with_lists(db, id=board_id)
    if not board:
        raise NotFoundException("Board not found")

    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    return board


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
        board_id: int,
        board_in: BoardUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> BoardResponse:
    """
    Actualizar un tablero
    """
    board = await board_crud.get(db, id=board_id)
    if not board:
        raise NotFoundException("Board not found")

    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    board = await board_crud.update(db, db_obj=board, obj_in=board_in)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
        board_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar un tablero
    """
    board = await board_crud.get(db, id=board_id)
    if not board:
        raise NotFoundException("Board not found")

    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    await board_crud.remove(db, id=board_id)
    return None

