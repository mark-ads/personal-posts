from fastapi import APIRouter
from sqlmodel import select

from src.models import PostCompleted, PostResponse, Posts, Post, PostResponseAdmin
from src.api.deps import PostDep, SessionDep, IsUserDep, is_admin

router = APIRouter(prefix='/posts', tags=['posts'])


@router.post('/', response_model=PostResponse)
async def create_post(session: SessionDep, post: Post, user: IsUserDep):
    post = Posts(text=post.text, author_id=user.id)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.get('/', response_model=list[PostResponse])
async def read_users_posts(session: SessionDep, user: IsUserDep, skip: int = 0, limit: int = 10):
    result = await session.execute(
        select(Posts).where(Posts.author == user).offset(skip).limit(limit)
        )
    posts = result.scalars().all()
    return posts


@router.put('/{post_id}', response_model=PostResponse)
async def change_post(session: SessionDep, post: PostDep, update: Post, user: IsUserDep):
    post.text = update.text
    await session.commit()
    await session.refresh(post)
    return post


@router.patch('/{post_id}/completed', response_model=PostResponse)
async def check_completed(session: SessionDep, post: PostDep, update: PostCompleted):
    post.completed = update.completed
    await session.commit()
    await session.refresh(post)
    return post


@router.delete('/{post_id}', status_code=204)
async def delete_post(session: SessionDep, post: PostDep, user: IsUserDep):
    await session.delete(post)
    await session.commit()