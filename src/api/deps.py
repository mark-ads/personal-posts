from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlmodel import select
from jose import JWTError, jwt
from collections.abc import AsyncGenerator
from typing import Annotated

from src.core.database import async_session
from src.core.config import settings
from src.models import Posts, Users, User


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/users/login')

async def is_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> Users:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')
    return user

IsUserDep = Annotated[Users, Depends(is_user)]

async def is_admin(user: IsUserDep) -> Users:
    if user.superuser is False:
        raise HTTPException(status_code=403, detail='User is not admin')
    return user

AdminDep = Annotated[Users, Depends(is_admin)]

async def get_post(session: SessionDep, post_id: int, user: IsUserDep) -> Posts:
    result = await session.execute(select(Posts).where(Posts.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    if post.author_id != user.id and not user.superuser:
        raise HTTPException(status_code=403, detail='Post belongs to other user')
    return post

PostDep = Annotated[Posts, Depends(get_post)]