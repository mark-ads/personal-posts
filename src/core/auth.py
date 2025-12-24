from datetime import datetime, timedelta

from fastapi.exceptions import HTTPException
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.config import settings
from src.core.security import verify_password
from src.models import Users

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> Users:
    """Авторизовать пользователя."""
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")
    return user


def create_access_token(data: dict[str, str | int | datetime]) -> str:
    """Создать токен.
    
    Содержит username, token_version, expire_date.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt
