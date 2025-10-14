from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import ConflictException, UnauthorizedException
from app.db.session import get_db
from app.schemas import UserCreate, UserResponse, Token
from app.schemas.token import RefreshTokenRequest, TokenRefreshResponse
from app.crud.user import user as user_crud
from app.db.models.user import User
from app.api.deps import get_current_active_user, verify_refresh_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        *,
        db: AsyncSession = Depends(get_db),
        user_in: UserCreate
) -> UserResponse:
    """
    Registrar un nuevo usuario
    """
    user = await user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise ConflictException("Email already registered")

    user = await user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise ConflictException("Username already taken")

    user = await user_crud.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
        db: AsyncSession = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Login con email y password (OAuth2 compatible)

    Retorna access_token (válido 30 min) y refresh_token (válido 7 días)
    """
    user = await user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise UnauthorizedException("Incorrect email or password")

    if not user.is_active:
        raise UnauthorizedException("Inactive user")

    # Crear tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
        *,
        db: AsyncSession = Depends(get_db),
        refresh_request: RefreshTokenRequest
) -> Token:
    """
    Refrescar access token usando refresh token

    - Envía el refresh_token obtenido en el login
    - Retorna un nuevo access_token y opcionalmente un nuevo refresh_token
    - El refresh_token debe ser válido (no expirado)
    """
    # Verificar el refresh token
    user_id = verify_refresh_token(refresh_request.refresh_token)

    # Verificar que el usuario existe y está activo
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("Inactive user")

    # Crear nuevo access token
    new_access_token = create_access_token(data={"sub": str(user.id)})

    # Opción 1: Retornar solo nuevo access_token (refresh_token sigue siendo el mismo)
    # return TokenRefreshResponse(
    #     access_token=new_access_token,
    #     token_type="bearer"
    # )

    # Opción 2: Token rotation - crear nuevo refresh_token también (más seguro)
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Obtener usuario actual
    """
    return current_user
