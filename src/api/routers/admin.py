from fastapi import APIRouter, Depends
from sqlmodel import select

from src.api.deps import SessionDep, is_admin
from src.models import PostResponseAdmin, Posts

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/posts", dependencies=[Depends(is_admin)], response_model=list[PostResponseAdmin]
)
async def read_all_posts(session: SessionDep, skip: int = 0, limit: int = 10):
    result = await session.execute(select(Posts).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts

