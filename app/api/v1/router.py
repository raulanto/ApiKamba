from fastapi import APIRouter
from app.api.v1.endpoints import auth, boards, lists, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(boards.router, prefix="/boards", tags=["boards"])
api_router.include_router(lists.router, prefix="/lists", tags=["lists"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
