from typing import List as TypingList
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.db.session import get_db
from app.db.models.user import User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskMove

from app.crud.task import task as task_crud
from app.crud.list import list_crud
from app.crud.board import board as board_crud

router = APIRouter()


async def verify_list_permission(
        db: AsyncSession, list_id: int, user_id: int
) -> None:
    """Helper para verificar permisos sobre una lista"""
    list_obj = await list_crud.get(db, id=list_id)
    if not list_obj:
        raise NotFoundException("List not found")

    board = await board_crud.get(db, id=list_obj.board_id)
    if board.owner_id != user_id:
        raise ForbiddenException("Not enough permissions")


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        *,
        db: AsyncSession = Depends(get_db),
        task_in: TaskCreate,
        current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """
    Crear una nueva tarea en una lista
    """
    await verify_list_permission(db, task_in.list_id, current_user.id)
    task = await task_crud.create(db, obj_in=task_in)
    return task


@router.get("/list/{list_id}", response_model=TypingList[TaskResponse])
async def list_tasks(
        list_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> TypingList[TaskResponse]:
    """
    Listar todas las tareas de una lista
    """
    await verify_list_permission(db, list_id, current_user.id)
    tasks = await task_crud.get_by_list(db, list_id=list_id)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """
    Obtener una tarea específica
    """
    task = await task_crud.get(db, id=task_id)
    if not task:
        raise NotFoundException("Task not found")

    await verify_list_permission(db, task.list_id, current_user.id)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """
    Actualizar una tarea
    """
    task = await task_crud.get(db, id=task_id)
    if not task:
        raise NotFoundException("Task not found")

    await verify_list_permission(db, task.list_id, current_user.id)
    task = await task_crud.update(db, db_obj=task, obj_in=task_in)
    return task


@router.post("/{task_id}/move", response_model=TaskResponse)
async def move_task(
        task_id: int,
        move_data: TaskMove,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """
    Mover una tarea a otra lista (cambiar de estado)
    """
    task = await task_crud.get(db, id=task_id)
    if not task:
        raise NotFoundException("Task not found")

    # Verificar permisos en la lista origen
    await verify_list_permission(db, task.list_id, current_user.id)

    # Verificar permisos en la lista destino
    await verify_list_permission(db, move_data.list_id, current_user.id)

    # Mover la tarea
    task = await task_crud.move_to_list(
        db, task=task, list_id=move_data.list_id, position=move_data.position
    )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar una tarea
    """
    task = await task_crud.get(db, id=task_id)
    if not task:
        raise NotFoundException("Task not found")

    await verify_list_permission(db, task.list_id, current_user.id)
    await task_crud.remove(db, id=task_id)
    return None