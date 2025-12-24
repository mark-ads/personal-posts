from fastapi import APIRouter, Depends
from sqlmodel import select

from src.api.deps import IsUserDep, PostDep, SessionDep, is_user
from src.models import Post, PostCompleted, PostResponse, Posts

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse)
async def create_post(session: SessionDep, post: Post, user: IsUserDep):
    """Создание поста."""
    post = Posts(text=post.text, author_id=user.id)  # type: ignore Требует так же подставить сюда created_at, который создается в Postgres
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def read_selected_post(post: PostDep):
    """Получение пользователем своего поста."""
    return post


@router.get("/", response_model=list[PostResponse])
async def read_users_posts(
    session: SessionDep, user: IsUserDep, skip: int = 0, limit: int = 10
):
    """Получение пользователем всех своих постов."""
    result = await session.execute(
        select(Posts).where(Posts.author == user).offset(skip).limit(limit)
    )
    posts = result.scalars().all()
    return posts


@router.put("/{post_id}", dependencies=[Depends(is_user)], response_model=PostResponse)
async def change_post(session: SessionDep, post: PostDep, update: Post):
    """Изменение пользователем своего поста."""
    post.text = update.text
    await session.commit()
    await session.refresh(post)
    return post


@router.patch("/{post_id}/completed", response_model=PostResponse)
async def check_completed(session: SessionDep, post: PostDep, update: PostCompleted):
    """Пометить пост выполненым."""
    post.completed = update.completed
    await session.commit()
    await session.refresh(post)
    return post


@router.delete("/{post_id}", dependencies=[Depends(is_user)], status_code=204)
async def delete_post(session: SessionDep, post: PostDep):
    """Удаление пользователем своего поста."""
    await session.delete(post)
    await session.commit()
