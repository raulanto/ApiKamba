from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse
from app.schemas.token import Token, TokenPayload, RefreshTokenRequest, TokenRefreshResponse
from app.schemas.board import BoardBase, BoardCreate, BoardUpdate, BoardResponse, BoardWithLists
from app.schemas.list import ListBase, ListCreate, ListUpdate, ListResponse, ListWithTasks
from app.schemas.task import TaskBase, TaskCreate, TaskUpdate, TaskMove, TaskResponse

# Resolver referencias circulares
BoardWithLists.model_rebuild()
ListWithTasks.model_rebuild()

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    # Token
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "TokenRefreshResponse",
    # Board
    "BoardBase",
    "BoardCreate",
    "BoardUpdate",
    "BoardResponse",
    "BoardWithLists",
    # List
    "ListBase",
    "ListCreate",
    "ListUpdate",
    "ListResponse",
    "ListWithTasks",
    # Task
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskMove",
    "TaskResponse",
]
