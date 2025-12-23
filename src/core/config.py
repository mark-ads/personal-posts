import asyncio

from pydantic_settings import BaseSettings, SettingsConfigDict

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TOKEN_KEY: str
    ADMIN_PASS: str
    DROP_TABLE: bool

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SECRET_KEY(self):
        return self.TOKEN_KEY

    model_config = SettingsConfigDict(env_file="src/.env")


settings = Settings()  # type: ignore
