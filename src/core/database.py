from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings
from sqlalchemy import text
from src.models import Users, Posts
from src.core.security import hash_password

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=15)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_version():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT VERSION()'))
        print(f'{res.first()[0]}')


async def init_db():
    if not settings.DROP_TABLE:
        return

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all, checkfirst=True)

    user_admin = Users(username='admin', password=hash_password(settings.ADMIN_PASS), superuser=True)
    user_test = Users(username='Aurora', password=hash_password(settings.ADMIN_PASS))
    first_post = Posts(text='First nice post', author_id=1)
    second_post = Posts(text='Second nice post', author_id=2)
            
    async with async_session() as session:
        session.add_all([user_admin, user_test, first_post, second_post])
        await session.commit()