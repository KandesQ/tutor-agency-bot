import os

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from alembic.config import Config
from alembic import command

from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16", dbname="tutor_agency_bot_test") as postgres:
        os.environ["DB_HOST"] = postgres.get_container_host_ip()
        os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["DB_USER"] = postgres.username
        os.environ["DB_PASSWORD"] = postgres.password
        os.environ["DB_NAME"] = "tutor_agency_bot_test"

        alembic_cfg = Config("alembic.ini")

        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            postgres.get_connection_url()
        )
        command.upgrade(alembic_cfg, "head")

        # Alembic должен запускаться в синхронном режиме, поэтому меняю драйвер после миграций
        postgres.driver = "+asyncpg"

        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:8.4.0") as redis:
        os.environ["REDIS_HOST"] = redis.get_container_host_ip()
        os.environ["REDIS_PORT"] = str(redis.get_exposed_port(6379))


        yield redis


@pytest_asyncio.fixture(scope="function")
async def redis_client(redis_container):
    redis_client = Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379)
    )

    yield redis_client

    await redis_client.flushdb()
    await redis_client.aclose()


@pytest_asyncio.fixture(scope="function")
async def async_session_local(postgres_container):
    engine = create_async_engine(postgres_container.get_connection_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    yield async_session

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_local):
    async with async_session_local() as session:
        yield session
        await session.rollback()