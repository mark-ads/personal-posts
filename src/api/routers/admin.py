from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from src.api.deps import SessionDep, is_admin
from src.core.security import hash_password
from src.models import (
    AdminUserInfoResponse,
    PostResponseAdmin,
    Posts,
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    Users,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/", dependencies=[Depends(is_admin)], response_model=UserResponse)
async def create_user(session: SessionDep, user: UserCreate):
    """Создание пользователя администратором."""
    result = await session.execute(select(Users).where(Users.username == user.username))
    username_check = result.scalar_one_or_none()
    if username_check is not None:
        raise HTTPException(status_code=403, detail="Username already taken")
    if user.password != user.repeat_password:
        raise HTTPException(status_code=409, detail="Passwords don't match")
    hashed = hash_password(user.password)
    new_user = Users(username=user.username, password=hashed)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get(
    "/posts", dependencies=[Depends(is_admin)], response_model=list[PostResponseAdmin]
)
async def read_all_posts(session: SessionDep, skip: int = 0, limit: int = 10):
    """Просмотр всех постов всех пользователей."""
    result = await session.execute(select(Posts).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts


@router.put("/", dependencies=[Depends(is_admin)], response_model=AdminUserInfoResponse)
async def update_users_role(session: SessionDep, user: UserRoleUpdate):
    """Изменение роли пользователя администратором."""
    result = await session.execute(select(Users).where(Users.username == user.username))
    user_to_edit = result.scalar_one_or_none()
    if user_to_edit is None:
        raise HTTPException(status_code=404, detail="Username not found")
    user_to_edit.superuser = user.superuser
    session.add(user_to_edit)
    await session.commit()
    await session.refresh(user_to_edit)
    return user_to_edit


@router.get(
    "/{username}",
    dependencies=[Depends(is_admin)],
    response_model=AdminUserInfoResponse,
)
async def get_users_info(session: SessionDep, username: str):
    """Получения информации о пользователе администратором."""
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Username not found")
    return user


@router.delete("/{username}", dependencies=[Depends(is_admin)], status_code=204)
async def delete_user_by_admin(session: SessionDep, username: str):
    """Эндпоинт для удаления пользователя из БД администратором."""
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.add(user)
    await session.delete(user)
    await session.commit()
    return
