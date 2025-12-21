from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from src.api.deps import SessionDep, is_admin
from src.core.auth import authenticate_user, create_access_token
from src.core.security import hash_password
from src.models import User, UserCreate, Users

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", dependencies=[Depends(is_admin)], response_model=User)
async def create_user(session: SessionDep, user: UserCreate):
    result = await session.execute(select(Users).where(Users.username == user.username))
    username_check = result.scalar_one_or_none()
    if username_check is not None:
        raise HTTPException(status_code=403, detail="Username already taken")
    hashed = hash_password(user.password)
    user = Users(username=user.username, password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login")
async def login_user(
    session: SessionDep, credentials: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(credentials.username, credentials.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/", dependencies=[Depends(is_admin)], response_model=User)
async def delete_user(session: SessionDep, target: User):
    result = await session.execute(
        select(Users).where(Users.username == target.username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return user
