from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from src.models import PostResponse, Posts, Post, PostResponseAdmin, Users
from src.api.deps import SessionDep, AdminDep, IsUserDep, is_user, is_admin

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/posts', dependencies=[Depends(is_admin)], response_model=list[PostResponseAdmin])
async def read_all_posts(session: SessionDep, skip: int = 0, limit: int = 10):
    result = await session.execute(select(Posts).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts