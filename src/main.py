from fastapi import FastAPI
from enum import Enum
from src.posts.router import router as posts_router
from src.users.router import router as users_router

app = FastAPI()
app.include_router(posts_router, prefix='/api/v1')
app.include_router(users_router, prefix='/api/v1')