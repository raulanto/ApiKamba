from typing import List as TypingList
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.db.session import get_db
from app.db.models.user import User
from app.schemas import ListCreate, ListUpdate, ListResponse, ListWithTasks

from app.crud.list import list_crud
from app.crud.board import board as board_crud

router = APIRouter()


@router.post("/", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
        *,
        db: AsyncSession = Depends(get_db),
        list_in: ListCreate,
        current_user: User = Depends(get_current_active_user)
) -> ListResponse:
    """
    Crear una nueva lista (estado) en un tablero
    """
    # Verificar que el tablero existe y pertenece al usuario
    board = await board_crud.get(db, id=list_in.board_id)
    if not board:
        raise NotFoundException("Board not found")

    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    list_obj = await list_crud.create(db, obj_in=list_in)
    return list_obj


@router.get("/board/{board_id}", response_model=TypingList[ListResponse])
async def list_lists(
        board_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> TypingList[ListResponse]:
    """
    Listar todas las listas de un tablero
    """
    # Verificar permisos
    board = await board_crud.get(db, id=board_id)
    if not board:
        raise NotFoundException("Board not found")

    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    lists = await list_crud.get_by_board(db, board_id=board_id)
    return lists


@router.get("/{list_id}", response_model=ListWithTasks)
async def get_list(
        list_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> ListWithTasks:
    """
    Obtener una lista con todas sus tareas
    """
    list_obj = await list_crud.get_with_tasks(db, id=list_id)
    if not list_obj:
        raise NotFoundException("List not found")

    # Verificar permisos
    board = await board_crud.get(db, id=list_obj.board_id)
    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    return list_obj


@router.put("/{list_id}", response_model=ListResponse)
async def update_list(
        list_id: int,
        list_in: ListUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> ListResponse:
    """
    Actualizar una lista
    """
    list_obj = await list_crud.get(db, id=list_id)
    if not list_obj:
        raise NotFoundException("List not found")

    # Verificar permisos
    board = await board_crud.get(db, id=list_obj.board_id)
    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    list_obj = await list_crud.update(db, db_obj=list_obj, obj_in=list_in)
    return list_obj


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
        list_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar una lista y todas sus tareas
    """
    list_obj = await list_crud.get(db, id=list_id)
    if not list_obj:
        raise NotFoundException("List not found")

    # Verificar permisos
    board = await board_crud.get(db, id=list_obj.board_id)
    if board.owner_id != current_user.id:
        raise ForbiddenException("Not enough permissions")

    await list_crud.remove(db, id=list_id)
    return None