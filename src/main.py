from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers.admin import router as admin_router
from src.api.routers.posts import router as posts_router
from src.api.routers.users import router as users_router
from src.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
