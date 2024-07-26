import time
import asyncio
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.orm import metadata, start_mappers, clear_mappers
from config import settings


async def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            async with engine.connect() as conn:
                return conn
        except OperationalError:
            await asyncio.sleep(0.5)
    pytest.fail("Postgres never came up")


@pytest.fixture(scope="session")
async def postgres_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    await wait_for_postgres_to_come_up(engine)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    return engine


@pytest.fixture
async def postgres_session(postgres_db):
    start_mappers()
    async_session = sessionmaker(
        postgres_db, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with session.begin():
            yield session
    clear_mappers()


@pytest.fixture(autouse=True)
async def clean_database(postgres_db):
    """Clean up the database after each test"""
    async with postgres_db.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
