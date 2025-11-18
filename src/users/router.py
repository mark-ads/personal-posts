from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.users.schemas import UserPublic, UserCreate, User
from src.deps import get_current_user

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/', response_model=UserPublic)
async def create_user(user: UserCreate):
    return user

@router.post('/login', response_model=UserPublic)
async def login_user(credentials: OAuth2PasswordRequestForm = Depends()):
    user = User(username=credentials.username)
    return user

@router.delete('/', dependencies=[Depends(get_current_user)], response_model=UserPublic)
async def delete_user(target: User):
    user = target.model_dump()
    user.update({'authorized': False})
    return user