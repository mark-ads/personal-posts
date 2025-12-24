from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from src.api.deps import IsUserDep, SessionDep, is_authorized
from src.core.auth import authenticate_user, create_access_token
from src.core.security import hash_password
from src.models import TokenResponse, UserCreate, UserResponse, Users, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    session: SessionDep, user: UserCreate, auth: bool = Depends(is_authorized)
):
    """Регистрация пользователя."""
    if auth:
        raise HTTPException(status_code=403, detail="User is already logged in")
    result = await session.execute(select(Users).where(Users.username == user.username))
    username_check = result.scalar_one_or_none()
    if username_check is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    if user.password != user.repeat_password:
        raise HTTPException(status_code=409, detail="Passwords don't match")
    hashed = hash_password(user.password)
    new_user = Users(username=user.username, password=hashed)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login_user(
    session: SessionDep, credentials: OAuth2PasswordRequestForm = Depends()
):
    """Вход в аккаунт."""
    user = await authenticate_user(credentials.username, credentials.password, session)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(
        {"sub": user.username, "ver": user.token_version}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/delete", response_model=UserResponse)
async def delete_user_by_user(session: SessionDep, user: IsUserDep):
    """Удаление пользователем своего аккаунта."""
    user.is_active = False
    user.token_version += 1
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/logout", status_code=204)
async def logout_user(session: SessionDep, user: IsUserDep):
    """Выход из системы."""
    user.token_version += 1
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return


@router.patch("/", response_model=UserResponse)
async def edit_users_info_by_user(
    session: SessionDep, user: IsUserDep, target: UserUpdate
):
    """Изменение пользователем своей информации."""
    if target.password != target.repeat_password:
        raise HTTPException(status_code=409, detail="Passwords don't match")
    if user.username != target.username:
        result = await session.execute(
            select(Users).where(Users.username == target.username)
        )
        username_check = result.scalar_one_or_none()
        if username_check:
            raise HTTPException(status_code=409, detail="Username already taken")
        user.username = target.username
    hashed_pass = hash_password(target.password)
    user.password = hashed_pass
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
