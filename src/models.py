from datetime import datetime
from typing import List, Optional

from sqlmodel import Column, Field, Relationship, SQLModel, String, text  # type: ignore


class TokenResponse(SQLModel):
    """Схема возврата токена."""

    access_token: str = Field(description="JWT токен.")
    token_type: str = Field(description="Тип токена.")


class User(SQLModel):
    """Базовая схема пользователя."""

    username: str = Field(min_length=4, max_length=255)


class UserResponse(User):
    """Схема возврата информации о пользователе."""

    is_active: bool = Field(description="Активен ли аккаунт.")


class UserCreate(User):
    """Схема для регистрации пользователя."""

    password: str = Field(min_length=6, max_length=32)
    repeat_password: str = Field(min_length=6, max_length=32)


class UserUpdate(UserCreate):
    """Схема обновления информации пользователя."""

    pass


class UserRoleUpdate(User):
    """Схема изменения роли пользователя."""

    superuser: bool = Field(description='Является ли аккаунт администратором.')


class AdminUserInfoResponse(User):
    """Схема возврата информации пользователя для админинстратора."""

    id: int = Field(description='ID аккаунта.')
    superuser: bool = Field(description='Является ли аккаунт администратором.')
    is_active: bool = Field(description="Активен ли аккаунт.")


class Users(User, table=True):
    """ORM модель БД со всей информацией пользователя."""

    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    is_active: bool = Field(default=True)
    superuser: bool = Field(default=False)
    token_version: int = Field(default=0)
    posts: List["Posts"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "noload"}
    )


class Post(SQLModel):
    """Базовая схема поста."""

    text: str = Field(description='Основной текст поста.')


class PostCompleted(SQLModel):
    """Схема обновления поля completed."""

    completed: bool = Field(description='Считается ли пост выполенным.')


class PostResponse(Post):
    """Схема информации о посте."""

    id: int = Field(description='ID поста.')
    created_at: datetime = Field(description='Время публикации поста.')
    completed: bool = Field(description='Считается ли пост выполенным.')


class PostResponseAdmin(Post):
    """Схема возврата информации о посте для администратора."""

    id: int = Field(description='ID поста.')
    created_at: datetime = Field(description='Время публикации поста.')
    author_id: int = Field(description='ID автора поста.')
    completed: bool = Field(description='Считается ли пост выполенным.')


class Posts(Post, table=True):
    """ORM модель БД со всей информацией о постах."""

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(String, server_default=text("TIMEZONE('utc', NOW())"))
    )
    author_id: int = Field(foreign_key="users.id")
    completed: bool = False
    author: Optional["Users"] = Relationship(back_populates="posts")
