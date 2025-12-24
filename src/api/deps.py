from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.config import settings
from src.core.database import async_session
from src.models import Posts, Users


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
oauth2_scheme_errors_off = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login", auto_error=False
)


def decode_token(token: str) -> tuple[str, int]:
    """Декодировать токен."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_version = payload.get("ver")

        if not isinstance(username, str):
            raise HTTPException(status_code=401, detail="Invalid token")
        if not isinstance(token_version, int):
            raise HTTPException(status_code=401, detail="Invalid token")

    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    return username, token_version


async def is_authorized(
    session: SessionDep, token: str | None = Depends(oauth2_scheme_errors_off)
) -> bool:
    """Определить авторизацию пользователя без HTTPException."""
    if token is None:
        return False
    username, token_version = decode_token(token)
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if user is None or token_version != user.token_version or not user.is_active:
        return False
    return True


AuthorizedDep = Annotated[Users, Depends(is_authorized)]


async def is_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> Users:
    """Определить авторизован ли пользователь и вернуть его объект из БД."""
    username, token_version = decode_token(token)
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if user.token_version != token_version or not user.is_active:
        raise HTTPException(status_code=403, detail="User is not authorized")
    return user


IsUserDep = Annotated[Users, Depends(is_user)]


async def is_admin(user: IsUserDep) -> Users:
    """Определить является ли пользователь администратором.
    Вернуть объект пользователя.
    """
    if user.superuser is False:
        raise HTTPException(status_code=403, detail="User is not admin")
    return user


async def get_post(session: SessionDep, post_id: int, user: IsUserDep) -> Posts:
    """Определить является ли пользователь автором поста.
    Вернуть пост.
    """
    result = await session.execute(select(Posts).where(Posts.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id and not user.superuser:
        raise HTTPException(status_code=403, detail="Post belongs to other user")
    return post


PostDep = Annotated[Posts, Depends(get_post)]
