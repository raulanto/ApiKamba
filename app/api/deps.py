from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.crud.user import user as user_crud
from app.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id_str is None:
            raise UnauthorizedException("Could not validate credentials")

        # Verificar que sea un access token
        if token_type != "access":
            raise UnauthorizedException("Invalid token type")

        user_id = int(user_id_str)

    except (JWTError, ValueError, TypeError) as e:
        raise UnauthorizedException("Could not validate credentials")

    user = await user_crud.get(db, id=user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_refresh_token(token: str) -> int:
    """
    Verificar que el token sea un refresh token válido y retornar el user_id
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id_str is None:
            raise UnauthorizedException("Could not validate credentials")

        # Verificar que sea un refresh token
        if token_type != "refresh":
            raise UnauthorizedException("Invalid token type")

        return int(user_id_str)

    except (JWTError, ValueError, TypeError) as e:
        raise UnauthorizedException("Invalid refresh token")
