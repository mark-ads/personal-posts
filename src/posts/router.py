from fastapi import APIRouter, Depends
from src.posts.schemas import PostCreate, PostPublic
from src.deps import get_current_user, CurrentUser

router = APIRouter(prefix='/posts', tags=['posts'])

@router.post('/', dependencies=[Depends(get_current_user)], response_model=PostPublic)
async def create_post(post_in: PostCreate):
    post_in.text = f'{post_in.text}'
    return PostCreate(text=post_in.text)

@router.get('/', dependencies=[Depends(get_current_user)], response_model=PostPublic)
async def show_latest_posts(skip: int = 0, limit: int = 10):
    return PostPublic(text='asdfasdf')

@router.get('/today', dependencies=[Depends(get_current_user)], response_model=PostPublic)
async def read_todays_post():
    return PostPublic(text='Public')

@router.delete('/{post_id}', dependencies=[Depends(get_current_user)])
async def delete_post(post_id: str):
    post = PostPublic(text='Noice last words').model_dump()
    post['deleted'] = post_id
    return post