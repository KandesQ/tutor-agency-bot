import asyncio
import os

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/tutor_agency_bot"


engine = create_async_engine(DB_URL)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=True
)


async def run_migrations():
    def migrate(connection):
        alembic_cfg = Config("../alembic.ini")
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(migrate)


async def main():
    await run_migrations()


if __name__ == "__main__":
    asyncio.run(main())