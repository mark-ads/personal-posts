from typing import Annotated
from fastapi import Depends, HTTPException, status
from src.users.schemas import User

def check_user():
    return True

CheckDep = Annotated[bool, Depends(check_user)]

def get_current_user(is_user: CheckDep) -> User:
    if not is_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authenticated'
            )
    return User

CurrentUser = Annotated[User, Depends(get_current_user)]