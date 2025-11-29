from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta
from jose import jwt

from src.core.config import settings
from src.models import Users
from src.core.security import verify_password

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15

async def authenticate_user(username: str, password: str, session: AsyncSession) -> Users:
    result = await session.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict) -> dict:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

