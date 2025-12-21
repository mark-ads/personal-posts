from datetime import datetime
from typing import List, Optional

from sqlmodel import Column, Field, Relationship, SQLModel, String, text


class User(SQLModel):
    username: str = Field(min_length=4, max_length=255)


class UserCreate(User):
    password: str = Field(min_length=6, max_length=32)


class Users(User, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    superuser: bool = Field(default=False)
    posts: List["Posts"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "noload"}
    )


class Post(SQLModel):
    text: str


class PostCompleted(SQLModel):
    completed: bool


class PostResponse(Post):
    id: int
    created_at: datetime
    completed: bool


class PostResponseAdmin(Post):
    id: int
    created_at: datetime
    author_id: int
    completed: bool


class Posts(Post, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(String, server_default=text("TIMEZONE('utc', NOW())"))
    )
    author_id: int = Field(foreign_key="users.id")
    completed: bool = False
    author: Optional["Users"] = Relationship(back_populates="posts")
